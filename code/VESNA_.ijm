// Analyze Vascular System Batch Processing
// 2024-01-26 Magdalena Schüttler


// comments starting with '// ->' indicate parts of code that can be changed by the user, if desired 



// DIALOG WINDOW
Dialog.createNonBlocking("BAVS");
Dialog.setInsets(0, 0, 0);
Dialog.addMessage("Batch Analyze Vascular System");
Dialog.setInsets(15, 0, 0);
// -> default directories can be set in second argument
Dialog.addDirectory("input folder:", "");
Dialog.addDirectory("output folder:", "");

Dialog.setInsets(15, 50, 0);
BoxLabels = newArray("activate Batch Mode", "Measurement 1 Volume fraction", "generate 3D projections of skeletons", "Measurement 2 Skeleton length", "close all windows after processing", "Measurement 3 Junctions and Branch length");
// -> default checks can be altered in following array
BoxDefaults = newArray(true, true, false, true, true, true);
Dialog.addCheckboxGroup(3, 2, BoxLabels, BoxDefaults);


Dialog.setInsets(15, 50, 0);
Dialog.addCheckbox("save parameters in table?", true);
Dialog.setInsets(0, 0, 0);
ParNames = newArray("brightness minimum", "brightness maximum", "σ (Gaussian blur)", "size threshold (Analyze Particles)", "maximum filter radius", "minimum filter radius", "length threshold (Branch Pruning)");
Dialog.addNumber(ParNames[0], 0); 	// brightness minimum
Dialog.addNumber(ParNames[1], 120);	// brightness maximum
Dialog.addNumber(ParNames[2], 1.8); // Gaussian Blur
Dialog.addNumber(ParNames[3], 55); 	// Analyze Particles
Dialog.addNumber(ParNames[4], 3); 	// maximum filter
Dialog.addNumber(ParNames[5], 4); 	// minimum filter
Dialog.addNumber(ParNames[6], 20); 	// Branch-Pruning
Dialog.setInsets(0, 50, 0);

Dialog.show()

// document parameter values in table
inputDir = Dialog.getString();
outputDir = Dialog.getString();

checkBatch = Dialog.getCheckbox();
check1 = Dialog.getCheckbox();
checkProj = Dialog.getCheckbox();
check2 = Dialog.getCheckbox();
checkClose = Dialog.getCheckbox();
check3 = Dialog.getCheckbox();

checkTab = Dialog.getCheckbox();

if(checkTab==1) {
	ParTable = "parameter_values";
	Table.create(ParTable);
	p = "parameter";
	w = "value";
}

ParArray = newArray();
for (i=0; i<8; i++) {
	ParArray[i] = Dialog.getNumber();
	if(checkTab==1) {
		Table.set(p, i, ParNames[i], ParTable);
		Table.set(w, i, ParArray[i], ParTable);
	}
}

if(checkTab==1) {
	Table.update(ParTable);
	selectWindow(ParTable);
	saveAs("Results", outputDir+ParTable+".csv");
	if(checkClose==1) {
		run("Close");
	}
}

if(checkBatch==1) {
	setBatchMode(true);
}

list = getFileList(inputDir);
print("Number of files in input folder:", list.length);

// document file names in table
tablename = "file_names";
Table.create(tablename);
n = "nr";
d = "file name";




// LOOP
// the loop iteratively opens all files in input folder, processes them, generates measurements and saves results in output folder
for (i=0; i<list.length; i++) {
	
	// document file name in file_name table
	Table.set(n, i, (i+1), tablename);
	Table.set(d, i, list[i], tablename);
	Table.update(tablename);
	
	print("");
	print("File", (i+1), "is being processed...");
	
	inputPath = inputDir + list[i];
	run("Bio-Formats Importer", "open=[inputPath] autoscale color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT");
	
	
	// PREPROCESSING
	if(bitDepth()!=8) {
		run("8-bit");
	}
	
	setMinAndMax(ParArray[0], ParArray[1]);
	run("Apply LUT", "stack");
	run("Gaussian Blur 3D...", "x="+ParArray[2]+" y="+ParArray[2]+" z=1.0");
		
	// BINARIZATION
	run("Convert to Mask", "method=Yen background=Dark");
	
	// remove small artifacts
	run("Analyze Particles...", "size="+ParArray[3]+"-Infinity show=Masks stack");
	
	// close small holes and connect fragmented vessels
	run("Maximum 3D...", "x="+ParArray[4]+" y="+ParArray[4]+" z="+ParArray[4]);
	run("Minimum 3D...", "x="+ParArray[5]+" y="+ParArray[5]+" z="+ParArray[5]);
	
	// remove internal holes
	run("Fill Holes (Binary/Gray)");
			
	titleBinary = getTitle();
	selectWindow(titleBinary);
	rename(outputDir + "Binary-"+(i+1));
	saveAs("Tiff", outputDir + "Binary-"+(i+1));
	titleBinary = getTitle();
	
	print("Binarization is completed.");
	
	
	// MEASUREMENT 1 VOLUME FRACTION
	if(check1==1) {
		selectWindow(titleBinary);
		run("Analyze Regions 3D", "volume surface_area_method=[Crofton (13 dirs.)] euler_connectivity=6");
		print("\\Update: ");
		selectWindow("Binary-"+(i+1)+"-morpho");
		
		// create results table
		Table.rename("Binary-"+(i+1)+"-morpho", "Results");
		setResult("Label", 0, "Capillary volume (sqr microns)");
		setResult("Label", 1, "Stack volume (sqr microns)");
		setResult("Label", 2, "Volume fraction (%)");
		
		// measure volume
		Stack.getDimensions(sw, sh, sc, ss, sf);
		getVoxelSize(vw, vh, vd, vu);
		stackVol = sw*sh*ss*vw*vh*vd;
		setResult("Volume", 1, stackVol);
		
		volFrac = getResult("Volume", 0)/stackVol*100;
		setResult("Volume", 2, volFrac);
		
		updateResults();
		saveAs("Results", outputDir + "Results Volume Fraction"+-(i+1)+".csv");
		if(checkClose==1) {
			run("Close");
		}
		
		print("\\Update:Measurement 1 Volume Fraction completed.");
	}
	
	
	// SKELETONIZATION
	selectWindow(titleBinary);
	run("Duplicate...", "duplicate");
	run("Skeletonize (2D/3D)");
	rename(outputDir + "Skeleton-"+(i+1));
	titleSkeleton = getTitle();
	selectWindow(titleSkeleton);
	saveAs("Tiff", outputDir + "Skeleton-"+(i+1));
	titleSkeleton = getTitle();
	skelDir = outputDir+"Skeleton-"+(i+1)+".tif";
	if(checkClose==1) {
		close();
	}
	
	
	// prune branches
	sep = File.separator;
	fileToBsh = replace(skelDir, sep, "/");
	thrsh = ParArray[7];
	ToBsh = fileToBsh+";"+thrsh;
	
	// runMacro("Prune_Skeleton_Ends for BAVS.bsh", ToBsh);
	runMacro("VESNA_branch_pruning.bsh", ToBsh);
	close(titleSkeleton);
	open(outputDir+"Skeleton-"+(i+1)+".tif");
	titlePruned = getTitle();
	
	// 3D projection
	if(checkProj==1) {
		selectWindow(titlePruned);
		run("3D Project...", "projection=[Brightest Point] axis=Y-Axis slice=2 initial=0 total=360 rotation=10 lower=1 upper=255 opacity=0 surface=100 interior=50 interpolate");
		selectWindow("Projections of Skeleton-"+(i+1));
		saveAs("Tiff", outputDir+"Skeleton-"+(i+1)+" 3D.tif");
		if(checkClose==1) {
			run("Close");
		}
	}
	
	print("Skeletonization is completed.");
	
	
	// MEASUREMENT 2 VASCULAR LENGTH
	if(check2==1) {
		selectWindow(titlePruned);
		run("Analyze Regions 3D", "voxel_count surface_area_method=[Crofton (13 dirs.)] euler_connectivity=6");
		selectWindow("Skeleton-"+(i+1)+"-morpho");
		saveAs("Results", outputDir + "Results Vascular Length"+-(i+1)+".csv");
		if(checkClose==1) {
			run("Close");
		}
		
		print("Measurement 2 Vascular Length completed.");
	}
	
	// MEASUREMENT 3 JUNCTIONS AND BRANCH LENGTH
	if(check3==1) {
		selectWindow(titlePruned);
		run("Set Measurements...", "area mean min centroid perimeter area_fraction display redirect=None decimal=2");
		run("Analyze Skeleton (2D/3D)", "prune=none show"); // Tagged skeleton, Results und Branch information
		selectWindow("Results");
		saveAs("Results", outputDir + "Results Vascular Branches"+-(i+1)+".csv");
		if(checkClose==1) {
			run("Close");
		}
		
		selectWindow("Branch information");
		saveAs("Results", outputDir + "Branch information"+-(i+1)+".csv");
		if(checkClose==1){
			run("Close");
		}
		
		print("Measurement 3 Vascular Branches completed.");
	}
	
	// alle Bilder schließen
	if(checkClose==1) {
		close("*");
	}
	
	print("Processing of file "+(i+1)+" completed.");
	
		//waitForUser(" ", "Durchlauf abgeschlossen.");
}

selectWindow(tablename);
saveAs("Results", outputDir+tablename+".csv");
if(checkClose==1) {
	run("Close");
}

print("");
print("Processing of all files completed.");
print("");