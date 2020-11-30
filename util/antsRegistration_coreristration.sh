#!/bin/bash
t1brain=${1}
template=${2}
thisfolder=${3}
out_name=${4}


./antsInstallExample/install/bin/antsRegistration --dimensionality 3 --float 0 \
	--output [$thisfolder/$out_name,$thisfolder/${out_name}Warped.nii.gz] \
	--interpolation Linear \
        --winsorize-image-intensities [0.005,0.995] \
        --use-histogram-matching 0 \
	--initial-moving-transform [$template,$t1brain,1] \
        --transform Rigid[0.1] \
        --metric MI[$template,$t1brain,1,32,Regular,0.25] \
        --convergence [1000x500x250x100,1e-6,10] \
        --shrink-factors 8x4x2x1 \
	--smoothing-sigmas 3x2x1x0vox \
        --transform Affine[0.1] \
        --metric MI[$t1brain,$template,1,32,Regular,0.25] \
        --convergence [1000x500x250x100,1e-6,10] \
        --shrink-factors 8x4x2x1 \
        --smoothing-sigmas 3x2x1x0vox \
#        -x $brainlesionmask
