#!/usr/bin/env python
# coding: utf-8

# In[3]:


import os,glob,re,time
from subprocess import call, check_output


# In[23]:


#The directory should be organized as SampleID/Date/modality.
#ex) 12345255-20101010 -T1
#                      -T2
#                      -T1CE
#                      -FLAIR
#            -20121010 -T1
#                      -T2
#                      -T1CE
#                      -FLAIR


# In[4]:


def dir_rename(name_path,name):
    for a in name_path:
        b=f"{os.path.dirname(a)}/{name}"
        os.rename(a,b)

def DCMtoNII(data_path, new_dir_name):
    direc=os.path.dirname(data_path)
    dcm_paths = glob.glob(os.path.join(data_path, "*","*","*"))
    print(f'sample :{len(dcm_paths)/4}')
    print('dcm2nii start!!')
    for i in dcm_paths:
        new_dir = re.sub(os.path.basename(direc),new_dir_name,i)
        print(new_dir)
        call(["mkdir","-p",new_dir])
        call(["./util/dcm2niix","-o",f"{new_dir}/",i])
    print("dcm2nii is DONE")
        
def join_path(path, pattern1):# pattern2="", pattern3="", pattern4=""):
    return  glob.glob(os.path.join(path, pattern1))[0]#,pattern2,pattern3,pattern4))[0]

def reori(mri,out_direc,outname):
    call(["fslreorient2std",mri,f"{out_direc}/{outname}"]) #outname = reori
    
def antregi_to_T1(T1_reori,T1CE_reori,T1_out_direc,outname):
    call(["./util/antsRegistration_coreristration.sh",T1_reori,T1CE_reori,f"{T1_out_direc}/",outname])

def brainextracrion(T1,template,mask,direc):
    call(["./util/antsInstallExample/install/bin/antsBrainExtraction.sh","-d","3","-a",T1,"-e",template,"-m", mask,"-o",f"{direc}/"])
    
def Truncate(N4_TRUNCATED_IMAGE,T2_Warped):
    call(["./util/antsInstallExample/install/bin/ImageMath","3",N4_TRUNCATED_IMAGE,"TruncateImageIntensity",T2_Warped,"0.01","0.999","256"])
    
def N4biascorrection(N4_TRUNCATED_IMAGE,N4_CONVERGENCE_1,N4_BSPLINE_PARAMS,N4_CORRECTED_IMAGE):
    call(["./util/antsInstallExample/install/bin/N4BiasFieldCorrection","-d","3","-i",N4_TRUNCATED_IMAGE,"-s","4","-c",N4_CONVERGENCE_1,
          "-b",N4_BSPLINE_PARAMS,"-o",N4_CORRECTED_IMAGE,"--verbose","1"])

def brainextraction_with_mask_(N4_CORRECTED_IMAGE,T1CE_mask,BrainExtractionBrain_T2):
    call(["./util/antsInstallExample/install/bin/MultiplyImages","3",N4_CORRECTED_IMAGE, T1CE_mask, BrainExtractionBrain_T2 ])
    
def brainextraction_with_mask(N4_TRUNCATED_IMAGE,T2_Warped,N4_CONVERGENCE_1,N4_BSPLINE_PARAMS,N4_CORRECTED_IMAGE,T1CE_mask,BrainExtractionBrain_T2):
    
    Truncate(N4_TRUNCATED_IMAGE,T2_Warped)
    N4biascorrection(N4_TRUNCATED_IMAGE,N4_CONVERGENCE_1,N4_BSPLINE_PARAMS,N4_CORRECTED_IMAGE)
    brainextraction_with_mask_(N4_CORRECTED_IMAGE,T1CE_mask,BrainExtractionBrain_T2)


# In[5]:


direc_path = "./raw_multiple//" #raw data path
new_dir_name = "raw_multiple_nii/" 

sample_path = f'./{new_dir_name}/'
modal_lst = ["T1", "T2", "T1CE", "FLAIR"]
T1_pattern="T1"
T2_pattern="T2"
T1CE_pattern="T1CE"
FLAIR_pattern="FLAIR"
reori_outname="reori"
template = "./template/myTemplate_to_IXI_Warped.nii.gz"
mask = "./template/reori_T_template2_LPI_rescale.Mask.nii.gz"

N4_CONVERGENCE_1="[ 50x50x50x50,0.0000001 ]"
N4_BSPLINE_PARAMS="[ 200 ]"


# In[6]:


name_path_FLAIR = glob.glob(os.path.join(direc_path, "*","*","*FLAIR*"))
name_path_T1CE = glob.glob(os.path.join(direc_path, "*","*","*CE*"))

dir_rename(name_path_FLAIR,FLAIR_pattern)
dir_rename(name_path_T1CE,T1CE_pattern)


# dcm2nii

# In[ ]:


DCMtoNII(direc_path,new_dir_name)


# rename directory (optional)

# In[8]:


data_path = glob.glob(os.path.join(sample_path, "*","*"))
for z in data_path:
    date = os.path.basename(z)
    date2=date.replace("-","")
    date2_path=f"{os.path.dirname(z)}/{date2}"
    os.rename(z,date2_path)


# run

# In[ ]:



data_path = glob.glob(os.path.join(sample_path, "*","*"))# *,* =sub, date
error_lst = []
try:
    for i in data_path:
        T1=glob.glob(os.path.join(i, T1_pattern,"*.nii"))
        T2=glob.glob(os.path.join(i, T2_pattern,"*.nii"))
        T1CE=glob.glob(os.path.join(i, T1CE_pattern,"*.nii"))
        FLAIR=glob.glob(os.path.join(i, FLAIR_pattern,"*.nii"))

        T1_out_direc=glob.glob(os.path.join(i, T1_pattern))[0]
        T2_out_direc=glob.glob(os.path.join(i, T2_pattern))[0]
        T1CE_out_direc=glob.glob(os.path.join(i, T1CE_pattern))[0]
        FLAIR_out_direc=glob.glob(os.path.join(i, FLAIR_pattern))[0]

        T1CE_mask = f"{T1CE_out_direc}/BrainExtractionMask.nii.gz"

        print(f"start !!! {i} preprocessing" )
        start = time.time()

        if len(T2)==0 or len(T1)==0 or len(T1CE)==0 or len(FLAIR)==0:
            print(f"******somthing is not exist in {i}")
            error_lst.append(i)
            continue

        if os.path.isfile(T1CE_mask) == True:
            print(f"******{T1CE_mask} is already exist")
            continue

        reori_outname_T1=f"{reori_outname}_{modal_lst[0]}"
        reori_outname_T2=f"{reori_outname}_{modal_lst[1]}"
        reori_outname_T1CE=f"{reori_outname}_{modal_lst[2]}"
        reori_outname_FLAIR=f"{reori_outname}_{modal_lst[3]}"
        print(FLAIR_out_direc)

        print(f"{modal_lst[0]} reorientation start")
        reori(T1[0],T1_out_direc,reori_outname_T1)
        print(f"{modal_lst[1]} reorientation start")
        reori(T2[0],T2_out_direc,reori_outname_T2)
        print(f"{modal_lst[2]} reorientation start")
        reori(T1CE[0],T1CE_out_direc,reori_outname_T1CE)
        print(f"{modal_lst[3]} reorientation start")
        reori(FLAIR[0],FLAIR_out_direc,reori_outname_FLAIR)



        print("co-registration start")   
        T1_reori = f"{T1_out_direc}/{reori_outname_T1}.nii.gz"
        T2_reori = f"{T2_out_direc}/{reori_outname_T2}.nii.gz"
        T1CE_reori = f"{T1CE_out_direc}/{reori_outname_T1CE}.nii.gz"
        FLAIR_reori = f"{FLAIR_out_direc}/{reori_outname_FLAIR}.nii.gz"
        antregi_to_T1(T1_reori,T1CE_reori,T1_out_direc,"reori_T1_")
        antregi_to_T1(T2_reori,T1CE_reori,T2_out_direc,"reori_T2_")
        antregi_to_T1(FLAIR_reori,T1CE_reori,FLAIR_out_direc,"reori_FLAIR_")
#         call(["/data/ml_shared/data_llb1600/script/antsRegistration_coreristration.sh",T2_reori,T1CE_reori,f"{T2_out_direc}/","reori_T2_"])


        print("start brain_extraction_T1CE")
        brainextracrion(T1CE_reori,template,mask,T1CE_out_direc)

        print("start brain_extraction_T1")
        T1_Warped = f"{T1_out_direc}/reori_T1_Warped.nii.gz"

        N4_TRUNCATED_IMAGE=f"{T1_out_direc}/N4Truncated_T1.nii.gz"
        N4_CORRECTED_IMAGE=f"{T1_out_direc}/N4Corrected_T1.nii.gz"
        BrainExtractionBrain_T1=f"{T1_out_direc}/BrainExtractionBrain_T1.nii.gz"

        brainextraction_with_mask(N4_TRUNCATED_IMAGE,T1_Warped,N4_CONVERGENCE_1,
                                  N4_BSPLINE_PARAMS,N4_CORRECTED_IMAGE,T1CE_mask,BrainExtractionBrain_T1)
        if os.path.isfile(BrainExtractionBrain_T1) == False:
            print(" ***************BrainExtractionBrain_T1 is fail***************")
            break

        print("start brain_extraction_T2")
        T2_Warped = f"{T2_out_direc}/reori_T2_Warped.nii.gz"
        N4_TRUNCATED_IMAGE=f"{T2_out_direc}/N4Truncated_T2.nii.gz"
        N4_CORRECTED_IMAGE=f"{T2_out_direc}/N4Corrected_T2.nii.gz"
        BrainExtractionBrain_T2=f"{T2_out_direc}/BrainExtractionBrain_T2.nii.gz"
        brainextraction_with_mask(N4_TRUNCATED_IMAGE,T2_Warped,N4_CONVERGENCE_1,
                                  N4_BSPLINE_PARAMS,N4_CORRECTED_IMAGE,T1CE_mask,BrainExtractionBrain_T2)
        if os.path.isfile(BrainExtractionBrain_T2) == False:
            print(" ***************BrainExtractionBrain_T2 is fail***************")
            break

        print("start brain_extraction_FLAIR")
        FLAIR_Warped = f"{FLAIR_out_direc}/reori_FLAIR_Warped.nii.gz"
        N4_TRUNCATED_IMAGE=f"{FLAIR_out_direc}/N4Truncated_FLAIR.nii.gz"
        N4_CORRECTED_IMAGE=f"{FLAIR_out_direc}/N4Corrected_FLAIR.nii.gz"
        BrainExtractionBrain_FLAIR=f"{FLAIR_out_direc}/BrainExtractionBrain_FLAIR.nii.gz"

        brainextraction_with_mask(N4_TRUNCATED_IMAGE,FLAIR_Warped,N4_CONVERGENCE_1,
                                  N4_BSPLINE_PARAMS,N4_CORRECTED_IMAGE,T1CE_mask,BrainExtractionBrain_FLAIR)
        if os.path.isfile(BrainExtractionBrain_FLAIR) == False:
            print(" ***************BrainExtractionBrain_FLAIR is fail***************")
            break

        print("time:", time.time() - start)

except:
    print("Ooh Noooooooooooooooooo!!!")
#     server.starttls()
#     server.login(email_user,email_password)

#     server.sendmail(email_user,email_send,text)
#     server.quit()
print(f'All preprocessing is done. But {error_lst} has a problem.'  )
    
    
    
    
    

