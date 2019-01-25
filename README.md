# nyc-visual-building-annotator

Many if not most of us have looked at the awe-inspiring New York City skyline and been curious about each building and its history. We believe that people are unable to fully appreciate the skyline without knowing this information. We sought to change this. Our program attempts to identify buildings within images of the New York City skyline taking in only smartphone data and a 3D model. By converting the phone data into the model space, we were able to create a projection of what the building are suppose to look like at a given location. Using alignment techniques, we were then able to outline the building and provide relevant information. We believe we have set the framework for an innovative application.


### Results

![alt text](https://raw.githubusercontent.com/roop-pal/nyc-visual-building-annotator/master/results.png)


### Final Report

Read our final report in "final_report.pdf"

### How to run
Download the 3d model from [here](http://maps.nyc.gov/download/3dmodel/DA_WISE_GML.zip).

Save `DA12_3D_Buildings_Merged.gml` in the directory.

Install requirements by running `pip install -r requirements.txt`

Run `python main.py` to generate 4 test examples.
