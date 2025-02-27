# VESNA

VESNA (Vessel Segmentation and Network Analysis) is a macro for the open-source image processing software Fiji/ImageJ enabling the segmentation, skeletonization and quantification of vascular networks.

***[doi]***

***[other badges?]***

***[also reference [lacan/Olivier Burri](https://gist.github.com/lacan/0a12113b1497db86d7df3ef102efd34d) for original Branch Pruning script -> license]***

When using VESNA, please cite our publication: <br>
***[citation of the paper]***

Feel free to use the `citation.bib` file.



## Table of Contents

1. [Getting Started](#getting-started)
2. [How to Use](#how-to-use)
    1. [Parameter Adjustment](#parameter-adjustment) 
    2. [Advanced Adjustments](#advanced-adjustments)
3. [Contributing](#contributing)
4. [License](#license)




## Getting Started

To install VESNA, follow these steps:

1. **Install Fiji** from the [official website](https://imagej.net/software/fiji/downloads).
2. **Install VESNA**:

    - Download the `VESNA_.ijm` file from this repository. 
    - In Fiji, go to *Plugins>Install...* in the toolbar. In the window, select the `VESNA_.ijm` file and confirm. In the second window, click *Save*.
    - After restarting Fiji, VESNA will be available in the *Plugins* tab in the toolbar.

3. **Install Requirements**:

    - Download the `VESNA_branch_pruning.bsh` file from this repository and move it to this folder: `Fiji.app/macros/`.
    - To install Bio-Formats and MorphoLibJ directly from Fiji, go to *Help>Update...* to start the updater. Click *Manage Update Sites* and check **"Bio-Formats"** and **"IJPB-plugins"**, if they are not checked already, and confirm. After restarting Fiji, any newly installed packages are ready for use.




## How to Use

To use VESNA, follow these steps:

1. **Prepare the Input Folder**: Create a new folder anywhere on your computer and put any image files you want to process into the folder.

    - The input files can be any file format that the Bio-Formats importer can handle, including `.tif`, `.nd2`, `.lif`, and many more.
    - The input files should contain the unprocessed 3D microscopy images and only the vasculature-specific stain (e. g. CD31). Files with more than one channel cannot be processed with the currect version of VESNA.

2. **Prepare the Output Folder**: Create a new folder anywhere on your computer. The folder should be empty, as files if this folder may be overwritten during image processing.

3. **Run VESNA**: Open VESNA from the *Plugins* tab. In the dialog window, you can change the settings of the image processing:

    - Select the input and output folders.
    - Checking *Activate Batch Mode* processes the images without opening them as a window, which shortens processing time.
    - Checking *Generate 3D Projections of Skeletons* calculates and saves 3D projections of each skeleton. These are useful for visual assessment of the skeletonization quality.
    - Unchecking *Close all Windows after Processing* keeps the results tables and the images (if Batch Mode is deactivated) open after the processing is completed. This is not recommended for larger numbers of input files.
    - Each of the measurement sets can be deactivated.
    - Checking *Save Parameters in a Table* saves the utilized parameters in a table. It is strongly recommended to keep this checked.
    - Lastly, the parameters for image processing can be adjusted to the input files. An in-depth explanation on how to adjust the parameters to the input images, can be found in the next section [Parameter Adjustment](#parameter-adjustment).




### Parameter Adjustment

Each data set has its own unique properties, such as the fluorescence intensity, background fluorescence, noise, and level of detail. To ensure the quality of the image processing, the parameters need to be set individually for each set of images. 

- To start of, each set of images should be processed using the **default parameter settings**. The quality resulting binary and skeletonized images is then assessed visually and the recognized structures are compared to the input image. For this, the 3D projections of the skeletonized images are most useful.
- The **parameters** are then **adjusted** iteratively, until an adequate quality is achieved. For this, it is recommended to select a single representative image out of the set, to speed up the process. For large and detailed vessel structures, it can be helpful to crop this first image for this process.<br><br>

Below is a brief description of each parameter and how to assess the proper setting:

- **Brightness Parameters**: One of the first steps of the image processing is the brightness adjustment to increase the contrast. The lower and upper limits of the brightness adjustment are defined by the minimum and maximum brightness parameters. 

    To assess proper setting, the binary image is compared to the input image. Ideally, the entire vessel structure should be present in the binary image, while the detail of brighter regions should be preserved. Recognition of weakly fluorescing vessels can be improved by lowering the brightness maximum. Conversely, to improve definition, the brightness maximum and minimum can be increased. In practice, this balance might be difficult to achieve, especially in images exhibiting non-homogeneous fluorescence and high background fluorescence. In such cases, the implication of the Subtract Background function may improve the results.
    
- **$\sigma$ Parameter** and **Maximum and Minimum Filter Parameters**: The Gaussian blur recombines fragmented vessels and prevents small artifactual segments along the segments. The $\sigma$ value is proportional to the radius of the Gaussian blur. Similarly, the maximum and minimum filters act as a three-dimensional substitute for morphological closing and are used to reconnect fragmented vessels. The respective parameters define the radius of each filter in voxels.

    To test the parameter setting, the skeletonized image is compared to the input image. Ideally, no fragmented vessels or small artifacts are present, while the detail of the structures is maintained.

- **Analyze Particles Threshold**: To remove any small artifacts from the binary image, the Analyze Particles function is applied. The parameter defines the threshold in px below which objects are excluded.

    The binary and/or skeletonized image is compared to the input image. Small artifacts that are not connected to the rest of the structure should be removed, while correctly segmented structures are not removed.

- **Branch Pruning Threshold**: Short artifactual segments that are directly connected to the network are removed using a Branch Pruning function. The parameter defines the length threshold in pixels. 

    The parameter is set correctly, if the skeletonized image does not contain any artifactual segments connected the the rest of the structure, while correctly recognized segments are preserved.

### Advanced Adjustments

In the source code, some further options can be adjusted. For example, default values for the settings can be changed. This is especially useful for the input and output folders.

If the adjustment of the parameter values does not yield acceptable results, using a different thresholding method for binarization might be a viable option. Triangle and Moments thresholding methods have been found to work well as alternatives to the default Yen thresholding.




## Contributing

Contributions to VESNA are very welcome! If you have a feature request, bug report, or proposal, please open an issue.




## License

VESNA is licensed under the MIT license.
