
# import the necessary packages
from skimage.measure import compare_ssim
import argparse
import imutils
import cv2
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required, current_identity
from flask import Flask, request #import main Flask class and request object
from PIL import Image
import numpy as np
#import flask
import io, os, sys
import datetime
import glob
import flask
import cv2
import base64
sys.path.append(".")
import tkinter
#import cv2
import imutils
from werkzeug.utils import secure_filename

from security import authenticate, identity

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True # To allow flask propagating exception even if debug is set to false on app
app.secret_key = 'ch@ngEp0nd'
api = Api(app)

jwt = JWT(app, authenticate, identity)


class TemplateMatching(Resource):
    
    @jwt_required()
    def post(self):
        #Upload your Template
        image1= request.files['template']  
        image1.save(image1.filename)  
        
        template = cv2.imread(image1.filename)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template = cv2.Canny(template, 50, 200)
        (tH, tW) = template.shape[:2]
        #upload multiple filees
        uploaded_files = request.files.getlist("file")
        for file in uploaded_files:
            # Check if the file is one of the allowed types/extensions
            file.save(secure_filename(file.filename))
            image = cv2.imread(file.filename)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            found = None
            # loop over the scales of the image
            for scale in np.linspace(0.2, 1.0, 20)[::-1]:
                # resize the image according to the scale, and keep track
                # of the ratio of the resizing
                resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
                r = gray.shape[1] / float(resized.shape[1])
                # if the resized image is smaller than the template, then break
                # from the loop
                if resized.shape[0] < tH or resized.shape[1] < tW:
                    break

                # detect edges in the resized, grayscale image and apply template
                # matching to find the template in the image
                edged = cv2.Canny(resized, 50, 200)
                result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
                (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

                # check to see if the iteration should be visualized
                    # draw a bounding box around the detected region
                clone = np.dstack([edged, edged, edged])
                cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                    (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
                
               # if we have found a new maximum correlation value, then ipdate
               # the bookkeeping variable
                if found is None or maxVal > found[0]:
                    found = (maxVal, maxLoc, r)

             # unpack the bookkeeping varaible and compute the (x, y) coordinates
             # of the bounding box based on the resized ratio
            (_, maxLoc, r) = found
            (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
            (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

            # draw a bounding box around the detected result and display the image
            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
            cv2.imshow("Image", image)
            cv2.waitKey(0)
            #Path to save the output images
            path = 'C:/Users/malini.d/Desktop/API_tm_SSIM/Template_Matching_API/Final_output_images'
            cv2.imwrite(os.path.join(path , file.filename), image)
            cv2.waitKey(0)
        return 'File saved Successfully!!!'        
		
api.add_resource(TemplateMatching, '/templatematch')

if __name__ == '__main__':
    app.run(debug=True)  # important to mention debug=True