from glob import glob
import math
import matplotlib as mpl
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from scipy import stats


def get_measurement(folder):
    '''
    Read measurements from VESNA results files

    parameters:
        folder: path to folder containing VESNA measurements
    
    returns:
        dict:   dictionary containing lists of measurement data
    '''

    dict = {        # gets filled with measurement data
        'volfrac': [],
        'totallen': [],
        'nseg': [], 'nskel': [], 'njunc': [], 'nend': [],
        'seglen': []
    }

    files = glob(os.path.join(folder, 'Results Volume fraction-*.csv'))

    for i in range(0, len(files)):
        f = os.path.basename(files[i]).removeprefix('Results Volume fraction-').removesuffix('.csv')     # get measurement number

        # stack volume in mm³
        stackvol = pd.read_csv(folder+'Results Volume fraction-'+str(f)+'.csv', index_col=' ').loc[2, 'Volume']/1000000000
        # volume fraction in %
        dict['volfrac'].append(pd.read_csv(folder+'Results Volume fraction-'+str(f)+'.csv', index_col=' ').loc[3, 'Volume'])

        # network length in 10^4 voxels
        dict['totallen'].append(pd.read_csv(folder+'Results Vascular length-'+str(f)+'.csv').loc[0, 'VoxelCount']/10000)

        # segment number in 1/mm³
        dict['nseg'].append(pd.read_csv(folder+'Results Vascular branches-'+str(f)+'.csv').loc[:, '# Branches'].sum()/stackvol)

        # skeleton number in 1/mm³
        dict['nskel'].append(pd.read_csv(folder+'Branch information-'+str(f)+'.csv').iloc[-1, 0]/stackvol)

        # junction number in 1/mm³
        dict['njunc'].append(pd.read_csv(folder+'Results Vascular branches-'+str(f)+'.csv').loc[:, '# Junctions'].sum()/stackvol)

        # endpoint number in 1/mm³
        dict['nend'].append(pd.read_csv(folder+'Results Vascular branches-'+str(f)+'.csv').loc[:, '# End-point voxels'].sum()/stackvol)

        # segment lengths in
        dict['seglen'].extend(pd.read_csv(folder+'Branch information-'+str(f)+'.csv').loc[:, 'Branch length'])
    
    return dict


def mwu_test(reference_group, test_group, significance=0.05):
    '''
    Perform a Mann-Whitney U test to test significance of two groups

    parameters:
        reference_group:    list of measurements of the reference group
        test_group:         list of measurements of the tested group
        significance:       level of significance alpha
    
    returns:
        marker:         '*' if the difference is significant, otherwise ''
    '''

    _, p = stats.mannwhitneyu(x=reference_group, y=test_group, nan_policy='omit')
    if p < significance:
        return '*'
    else:
        return ''


def glass_delta(reference_group, test_group):
    '''
    Calculate Glass's Δ effect size of two groups

    parameters:
        reference_group:        list of measurements of the reference group
        test_group:             list of measurements of the tested group
    
    returns:
        delta:      effect size of the two groups
    '''

    ref_mean = np.mean(reference_group)
    test_mean = np.mean(test_group)

    delta = abs(ref_mean-test_mean) / (math.sqrt(np.std(reference_group)**2))

    return delta


def plot_measurements(input_paths, labels, ref_group=0, legend=True, colors=['#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499'], test=True, save=[], layout='horizontal'):
    '''
    Plot measurements of one or more groups as box plots
    
    paramters:
        input_paths:    list of paths to folders containing VESNA measurements
        labels:         list of group labels to be displayed in the legend
        ref_group:      index of reference group in input_paths list to be used as reference for significance test
        legend:         if True, legend is displayed in the figure
        colors:         list of colors to be used for the box plot
        test:           if True, Mann-Whitney U test is performed and significance is marked with * in plots
        save:           if filepath, figure is saved to this path. if any other value, figure is not saved
        layout:         select output plot layout: 'horizontal', 'vertical'
    
    returns:
        bonferroni:     bonferroni-corrected level of significance
        glass:          dataframe containing Glass's Δ effect sizes
    '''

    # check correct layout value
    if not layout in ['horizontal', 'vertical']:
        print('Layout argument does not have a valid value.')
        return 

    # read measurements

    dict_list = []      # gets filled with dictionaries

    for path in input_paths:
        temp = get_measurement(path)
        dict_list.append(temp)

    # test significance 

    if test:
        markers = {        # gets filled with significance markers for plot
            'volfrac': [],
            'totallen': [],
            'nseg': [], 'nskel': [], 'njunc': [], 'nend': [],
            'seglen': []
        }
        keys = list(markers.keys())

        bonferroni = 0.05/(len(input_paths)-1)
        print('Bonferroni-corrected level of significance:', bonferroni)

        for i in range(0, len(input_paths)):
            if i != ref_group:
                for k in keys:
                    temp = mwu_test(
                        reference_group=dict_list[ref_group][k], 
                        test_group=dict_list[i][k], 
                        significance=bonferroni)
                    markers[k].append(temp)
    
    # create box plot

    measurement_labels = [
        'volume fraction \n[%]', 
        'network length \n[10$^4$ voxels]', 
        'segments [mm$^-$$^3$]', 
        'skeletons [mm$^-$$^3$]', 
        'junctions [mm$^-$$^3$]', 
        'end points [mm$^-$$^3$]', 
        'segment lengths [μm]']
    
    keys = list(dict_list[0].keys())
    labels = [labels[l]+' (n='+str(len(dict_list[l][keys[0]]))+')' for l in range(0, len(labels))]

    if layout == 'horizontal':
        fig = plt.figure(figsize=(10, 4.5))
        gs = GridSpec(2, 4, figure=fig, wspace=0.7, hspace=0.2)

        ax_vf      = fig.add_subplot(gs[0,0])  # define subplot positions
        ax_vl      = fig.add_subplot(gs[1,0])
        ax_vb_bsum = fig.add_subplot(gs[0,1])
        ax_vb_skel = fig.add_subplot(gs[1,1])
        ax_vb_junc = fig.add_subplot(gs[0,2])
        ax_vb_ends = fig.add_subplot(gs[1,2])
        ax_vl_seg  = fig.add_subplot(gs[:,3])

    elif layout == 'vertical':
        fig = plt.figure(figsize=(4.5, 8.5))
        gs = GridSpec(4, 2, figure=fig, wspace=0.7, hspace=0.2)

        ax_vf      = fig.add_subplot(gs[0,0])  # define subplot positions
        ax_vl      = fig.add_subplot(gs[1,0])
        ax_vb_bsum = fig.add_subplot(gs[0,1])
        ax_vb_skel = fig.add_subplot(gs[1,1])
        ax_vb_junc = fig.add_subplot(gs[2,0])
        ax_vb_ends = fig.add_subplot(gs[3,0])
        ax_vl_seg  = fig.add_subplot(gs[2:,1])
    
    axes = [ax_vf, ax_vl, ax_vb_bsum, ax_vb_skel, ax_vb_junc, ax_vb_ends, ax_vl_seg]

    for a in range(0, len(axes)):
        ax = axes[a]
        key = keys[a]

        max_value = np.max([np.max(d[key]) for d in dict_list])
        if max_value >= 1000:         # rescale axes with very high values
            boxdata = [[value*0.001 for value in d[key]] for d in dict_list]
            measurement_labels[a] = measurement_labels[a].split('[')[0]+'[10$^4$'+measurement_labels[a].split('[')[1]
        else:
            boxdata = [d[key] for d in dict_list]
        # create boxes
        bp = ax.boxplot(
            boxdata,
            patch_artist=True,
            medianprops=dict(color='black'),
            sym='.',
            widths=0.5
        )
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        ax.set_ylabel(measurement_labels[a])
        ax.set_xticks([])

        # annotate significance with markers
        if test:
            j = 0  # flag for markers[key] containing at least one '*'
            for item in markers[key]:
                if item == '*':
                    j = 1
                    break

            if j == 1:  # only annotate, if any significance in this plot
                _, upper = ax.get_ylim()
                if a == 6:
                    ax.set_ylim(bottom=None, top=upper*1.1)
                else:
                    ax.set_ylim(bottom=None, top=upper*1.2)
                plt.draw()
                
                rects = ax.patches
                for rect, label in zip(rects, markers[key]):
                    # height = np.max(np.max(boxdata))
                    if a == 6:
                        ax.annotate(label,
                            xy=(0.5, 0.925), 
                            xycoords='axes fraction',
                            xytext=(0.5, 0.925),
                            textcoords='axes fraction',
                            va='bottom',
                            ha='center',
                            arrowprops=dict(arrowstyle='-[, widthB=2')
                        )
                    else:
                        ax.annotate(label,
                            xy=(0.5, 0.85), 
                            xycoords='axes fraction',
                            xytext=(0.5, 0.85),
                            textcoords='axes fraction',
                            va='bottom',
                            ha='center',
                            arrowprops=dict(arrowstyle='-[, widthB=2')
                        )
        
    # create legends
    if legend == True:  # format legend 
        patches = []
        for p in range(0, len(input_paths)):
            patches.append(mpatches.Patch(
                facecolor=colors[p],
                label=labels[p],
                edgecolor='black'))
        
        if layout == 'vertical':
            fig.legend(
                labels=labels, 
                handles=patches, 
                loc='upper center', 
                bbox_to_anchor=(0, 0.85, 1, 0.102),  # second argument can be adjusted for vertical position of legend
                ncol = 1,
                frameon = False)
        else:
            fig.legend(
                labels=labels, 
                handles=patches, 
                loc='upper center', 
                ncol = 2,
                frameon = False)
        
    try:
        plt.savefig(save, transparent=True, bbox_inches='tight')
    except:
        pass

    # calculate Glass's Δ effect size
    if test:
        glass = dict()

        for i, k in zip(range(0, len(input_paths)), keys):
            glass[k] = glass_delta(reference_group=dict_list[ref_group][k], test_group=dict_list[i][k])
        
        glass = pd.DataFrame(data=glass, index=['Glass\'s Δ (effect size)'])
        display(glass)
        
        return bonferroni, glass


def plot_measurements_doublebox(input_paths, labels, ticks, ref_group=0, legend=True, colors=['#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499'], save=[], layout='horizontal'):
    '''
    Plot measurements of one or more groups as box plots
    
    paramters:
        input_paths:    list of paths to folders containing VESNA measurements
        labels:         list of group labels to be displayed in the legend
        ticks:          list of tick labels to be displayed in the bottom subplots
        ref_group:      index of reference group in input_paths list to be used as reference for significance test
        legend:         if True, legend is displayed in the figure
        colors:         list of colors to be used for the box plot
        save:           if filepath, figure is saved to this path. if any other value, figure is not saved
        layout:         select output plot layout: 'horizontal', 'vertical'
    
    returns:
        bonferroni:     bonferroni-corrected level of significance
        glass:          dataframe containing Glass's Δ effect sizes
    '''

    # check correct layout value
    if not layout in ['horizontal', 'vertical']:
        print('Layout argument does not have a valid value.')
        return 

    # read measurements

    dict_list = []      # gets filled with dictionaries

    for path in input_paths:
        temp = get_measurement(path)
        dict_list.append(temp)

    # # test significance 

    # markers = {        # gets filled with significance markers for plot
    #     'volfrac': [],
    #     'totallen': [],
    #     'nseg': [], 'nskel': [], 'njunc': [], 'nend': [],
    #     'seglen': []
    # }
    # keys = list(markers.keys())

    # bonferroni = 0.05/(len(input_paths)-1)
    # print('Bonferroni-corrected level of significance:', bonferroni)

    # for i in range(0, len(input_paths)):
    #     if i != ref_group:
    #         for k in keys:
    #             temp = mwu_test(
    #                 reference_group=dict_list[ref_group][k], 
    #                 test_group=dict_list[i][k], 
    #                 significance=bonferroni)
    #             markers[k].append(temp)
    
    # create box plot

    measurement_labels = [
        'volume fraction \n[%]', 
        'network length \n[10$^4$ voxels]', 
        'segments [mm$^-$$^3$]', 
        'skeletons [mm$^-$$^3$]', 
        'junctions [mm$^-$$^3$]', 
        'end points [mm$^-$$^3$]', 
        'segment lengths [μm]']
    
    keys = list(dict_list[0].keys())

    labels = [labels[l]+' (n='+str(len(dict_list[l][keys[0]]))+')' for l in range(0, len(labels))]

    if layout == 'horizontal':
        fig = plt.figure(figsize=(10, 4.5))
        gs = GridSpec(2, 4, figure=fig, wspace=0.7, hspace=0.2)

        ax_vf      = fig.add_subplot(gs[0,0])  # define subplot positions
        ax_vl      = fig.add_subplot(gs[1,0])
        ax_vb_bsum = fig.add_subplot(gs[0,1])
        ax_vb_skel = fig.add_subplot(gs[1,1])
        ax_vb_junc = fig.add_subplot(gs[0,2])
        ax_vb_ends = fig.add_subplot(gs[1,2])
        ax_vl_seg  = fig.add_subplot(gs[:,3])

    elif layout == 'vertical':
        fig = plt.figure(figsize=(4.5, 8.5))
        gs = GridSpec(4, 2, figure=fig, wspace=0.7, hspace=0.2)

        ax_vf      = fig.add_subplot(gs[0,0])  # define subplot positions
        ax_vl      = fig.add_subplot(gs[1,0])
        ax_vb_bsum = fig.add_subplot(gs[0,1])
        ax_vb_skel = fig.add_subplot(gs[1,1])
        ax_vb_junc = fig.add_subplot(gs[2,0])
        ax_vb_ends = fig.add_subplot(gs[3,0])
        ax_vl_seg  = fig.add_subplot(gs[2:,1])
    
    axes = [ax_vf, ax_vl, ax_vb_bsum, ax_vb_skel, ax_vb_junc, ax_vb_ends, ax_vl_seg]

    for a in range(0, len(axes)):
        ax = axes[a]
        key = keys[a]

        max_value = np.max([np.max(d[key]) for d in dict_list])
        if max_value >= 1000:         # rescale axes with very high values
            boxdata = [[value*0.001 for value in d[key]] for d in dict_list]
            measurement_labels[a] = measurement_labels[a].split('[')[0]+'[10$^4$'+measurement_labels[a].split('[')[1]
        else:
            boxdata = [d[key] for d in dict_list]
        # create double boxes
        leftdata = boxdata[0::2]
        rightdata = boxdata[1::2]
        bp = ax.boxplot(        # left boxes
            leftdata,
            positions=[p-0.225 for p in range(0, int(len(input_paths)/2))],
            patch_artist=True,
            medianprops=dict(color='black'),
            sym='.',
            widths=0.4
        )
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        ax.set_ylabel(measurement_labels[a])
        ax.set_xticks([])
        bp = ax.boxplot(        # right boxes
            rightdata,
            positions=[p+0.225 for p in range(0, int(len(input_paths)/2))],
            patch_artist=True,
            medianprops=dict(color='black'),
            sym='.',
            widths=0.4
        )
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor((color, 0.35))
        ax.set_ylabel(measurement_labels[a])
        ax.set_xticks([])
        if layout == 'horizontal':
            if a in [1, 3, 5, 6]:
                ax.set_xticks(range(0, int(len(input_paths)/2)), ticks)
        elif layout == 'vertical':
            if a in [5, 6]:
                ax.set_xticks(range(0, int(len(input_paths)/2)), ticks)

        # # annotate significance with markers      ## removed

        # # manually annotate significance

        # if a == 6:
        #     _, upper = ax.get_ylim()
        #     ax.set_ylim(bottom=None, top=upper*1.1)

        #     ax.annotate('*',
        #         xy=(0.6, 0.925), 
        #         xycoords='axes fraction',
        #         xytext=(0.6, 0.925),
        #         textcoords='axes fraction',
        #         va='bottom',
        #         ha='center',
        #         arrowprops=dict(arrowstyle='-[, widthB=2')
        #     )


    # create legends
    if legend == True:  # format legend 
        patches = []
        patches.append(mpatches.Patch(
            facecolor=colors[0],
            label=labels[0],
            edgecolor='black'))
        patches.append(mpatches.Patch(
            facecolor= mpl.colors.to_rgba(colors[0], 0.35),
            label=labels[1],
            edgecolor='black'
        ))
        
        if layout == 'vertical':
            fig.legend(
                labels=labels, 
                handles=patches, 
                loc='upper center', 
                bbox_to_anchor=(0, 0.85, 1, 0.102),  # second argument can be adjusted for vertical position of legend
                ncol = 1,
                frameon = False)
        else:
            fig.legend(
                labels=labels, 
                handles=patches, 
                loc='upper center', 
                ncol = 2,
                frameon = False)
        
    try:
        plt.savefig(save, transparent=True, bbox_inches='tight')
    except:
        pass