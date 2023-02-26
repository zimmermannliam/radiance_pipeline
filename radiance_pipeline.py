import os
rp = __import__(__name__)
from radiance_data import RadianceData


def hdrgen(path_to_images, path_to_camera, rd):
# in    path_to_images    string with <location to images>/*.JPG
#       path_to_camera    string with <location to camera>/camera.rsp
# out   creates file output1.hdr
  return ("hdrgen {} -o {}/output1.hdr -r {} -a -e -f -g"
            .format(path_to_images, rd.path_temp, path_to_camera))

def pcompos(rd, step):
  return ("pcompos -x {x} -y {y} Intermediate/output{pstep}.hdr -{xleft} -{ydown} > \
  Intermediate/output{step}.hdr".format(x=rd.diameter, y=rd.diameter, xleft=rd.xleft, ydown=rd.ydown, 
                                        pstep = step - 1, step = step))

def pfilt(rd, step):
  return ("pfilt -1 -x {} -y {} {}/output{}.hdr > {}/output{}.hdr"
            .format(rd.targetx, rd.targety, rd.path_temp, step - 1, rd.path_temp, step))

def pcomb(cal_file, rd, step):
  return ("pcomb -f {} {}/output{}.hdr > {}/output{}.hdr"
          .format(cal_file, rd.path_temp, step - 1, rd.path_temp, step))

def radiance_pipeline(rd):

  diameter         = rd.diameter
  xleft            = rd.xleft
  ydown            = rd.ydown
  vv               = rd.vv
  vh               = rd.vh
  targetx          = rd.targetx
  targety          = rd.targety 
  paths_ldr        = rd.paths_ldr
  path_temp        = rd.path_temp
  path_rsp_fn      = rd.path_rsp_fn
  path_vignetting  = rd.path_vignetting
  path_fisheye     = rd.path_fisheye
  path_ndfilter    = rd.path_ndfilter
  path_calfact     = rd.path_calfact


  test_mode = False

  if test_mode:
    os.system(f"mv {path_temp}/output1.hdr /tmp")
    os.system(f"rm {path_temp}/*")
    os.system("mv /tmp/output1.hdr Intermediate/")
  else:
    os.system(f"rm {path_temp}/*")

    # Merging of exposures 
    os.system(hdrgen(" ".join(paths_ldr), 
                     path_rsp_fn, rd))

  # Nullifcation of exposure value
  os.system(f"ra_xyze -r -o {rd.path_temp}/output1.hdr > {rd.path_temp}/output2.hdr")


  # Cropping and resizing
  os.system(pcompos(rd, 3))

  # Vignetting correction
  os.system(pcomb(rd.path_vignetting, rd, 4))

  # Crop
  os.system(pfilt(rd, 5))

  # Projection adjustment
  os.system(pcomb(rd.path_fisheye, rd, 6))


  # ND Filter correction
  os.system(pcomb(rd.path_ndfilter, rd, 7))

  # Photometric adjustment
  # os.system(pcomb("Inputs/Parameters/CF_f5d6.cal", 8))
  os.system(f"pcomb -h -f {rd.path_calfact} {rd.path_temp}/output7.hdr > {rd.path_temp}"
             "/output8.hdr")

  # HDR image header editing
  header_step = 9
  os.system("(getinfo < {temp}/output{pstep}.hdr  \
             | sed \"/VIEW/d\" && getinfo - < {temp}/output{pstep}.hdr) \
             > {temp}/output{step}.hdr"
             .format(temp=rd.path_temp, pstep=header_step - 1, step=header_step))

  os.system("getinfo -a \"VIEW = -vta -vv {vv} -vh {vh}\" \
             < {temp}/output{pstep}.hdr > \
             {temp}/output{step}.hdr"
             .format(temp=rd.path_temp, vv=vv, vh=vh, pstep=header_step, 
                     step=header_step+1))
  
  # Validity check
  os.system("evalglare -V Intermediate/output10.hdr")


def main():
  rd = RadianceData(
  diameter = 3612,
  xleft = 1019,
  ydown = 74,
  vv = 186,
  vh = 186,
  targetx = 1000,
  targety = 1000,
  paths_ldr = ["Inputs/LDRImages/*.JPG"],
  path_temp = "Intermediate",
  path_rsp_fn = "Inputs/Parameters/Response_function.rsp",
  path_vignetting = "Inputs/Parameters/vignetting_f5d6.cal",
  path_fisheye = "Inputs/Parameters/fisheye_corr.cal",
  path_ndfilter = "Inputs/Parameters/NDfilter_no_transform.cal",
  path_calfact = "Inputs/Parameters/CF_f5d6.cal"
  )

  radiance_pipeline(rd)
  

if __name__ == "__main__":
  main()
