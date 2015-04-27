
import plone
import os,sys
import Image


def load_standardised_image( filename, path, width, height ):
	
	###
	### Load Image
	###

	image = Image.open("images/Our Photos/2015-04-22 19.01.17.jpg")

	print image.bits, image.size, image.format


	### 
	### Scale Image
	###

	new_image = plone.scale.scale.scaleImage(image, width=width, height=height)

	return new_image

