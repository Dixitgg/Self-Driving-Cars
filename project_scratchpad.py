# importing some useful packages
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
# matploylib inline

#   Some OpenCV functions (beyond those introduced in the lesson) that might be useful for this project are:
#
#   cv2.inRange()         for color selection
#
#       http://docs.opencv.org/2.4/modules/core/doc/operations_on_arrays.html?highlight=inrange#cv2.inRange
#
#
#   cv2.fillPoly()        for regions selection
#
#       http://docs.opencv.org/2.4/modules/core/doc/drawing_functions.html?highlight=fillpoly#cv2.fillPoly
#
#
#   cv2.line()            to draw lines on an image given endpoints
#
#       http://docs.opencv.org/2.4/modules/core/doc/drawing_functions.html?highlight=line#cv2.line
#
#
#   cv2.addWeighted()     to coadd / overlay two images cv2.cvtColor() to grayscale or change color cv2.imwrite() to
#                           output images to file
#
#       http://docs.opencv.org/2.4/modules/core/doc/operations_on_arrays.html?highlight=addweighted#cv2.addWeighted
#
#
#   cv2.bitwise_and()     to apply a mask to an image
#
#       http://docs.opencv.org/2.4/modules/core/doc/operations_on_arrays.html?highlight=bitwise_and#cv2.bitwise_and
#
#
#   Check out the OpenCV documentation to learn about these and discover even more awesome functionality!
#
#
#   Below are some helper functions to help get you started. They should look familiar from the lesson!
#
#   from helpers import FUNCTION_NAME

import math


def grayscale(img):
    """Applies the Grayscale transform
    This will return an image with only one color channel
    but NOTE: to see the returned image as grayscale
    you should call plt.imshow(gray, cmap='gray')"""
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def canny(img, low_threshold, high_threshold):
    """Applies the Canny transform"""
    return cv2.Canny(img, low_threshold, high_threshold)


def gaussian_noise(img, kernel_size):
    """Applies a Gaussian Noise kernel"""
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)


def region_of_interest(img, vertices):
    """
    Applies an image mask.

    Only keeps the region of the image defined by the polygon
    formed from `vertices`. The rest of the image is set to black.
    """
    # defining a blank mask to start with
    mask = np.zeros_like(img)

    # defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255

    # filling pixels inside the polygon defined by "vertices" with the fill color
    cv2.fillPoly(mask, vertices, ignore_mask_color)

    # returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


def draw_lines(img, lines, color=[255, 0, 0], thickness=5):
    """
    NOTE: this is the function you might want to use as a starting point once you want to
    average/extrapolate the line segments you detect to map out the full
    extent of the lane (going from the result shown in raw-lines-example.mp4
    to that shown in P1_example.mp4).

    Think about things like separating line segments by their
    slope ((y2-y1)/(x2-x1)) to decide which segments are part of the left
    line vs. the right line.  Then, you can average the position of each of
    the lines and extrapolate to the top and bottom of the lane.

    This function draws `lines` with `color` and `thickness`.
    Lines are drawn on the image inplace (mutates the image).
    If you want to make the lines semi-transparent, think about combining
    this function with the weighted_img() function below
    """

    sides = [[], []]

    for line in lines:
        for x1, y1, x2, y2 in line:
            # ignore horizontal lines below a certain angle
            angle = math.atan2(y2 - y1, x2 - x1) * 180.0 / np.pi
            if -45 < angle <= -30:
                # negative angle is left line
                # print('(side,x1,y1,x2,y2,angle) = (', 'L',',', x1, ',', y1, ',', x2, ',', y2, ',', angle, ')')
                sides[0].append(tuple((x1, y1, x2, y2, angle)))

                # cv2.line(img, (x1, y1), (x2, y2), color, thickness)
            elif 25 < angle <= 45:
                # positive angle is right line
                # print('(side,x1,y1,x2,y2,angle) = (', 'R', ',', x1, ',', y1, ',', x2, ',', y2, ',', angle, ')')
                sides[1].append(tuple((x1, y1, x2, y2, angle)))
                # cv2.line(img, (x1, y1), (x2, y2), color, thickness)
            else:
                print('XXX (side,x1,y1,x2,y2,angle) = (', 'R', ',', x1, ',', y1, ',', x2, ',', y2, ',', angle, ')')

    # draw left line
    all_x1 = []
    all_y1 = []
    all_x2 = []
    all_y2 = []

    for x1, y1, x2, y2, angle in sides[0]:
        all_x1.append(x1)
        all_x2.append(x2)
        all_y1.append(y1)
        all_y2.append(y2)

    avg_x1 = sum(all_x1) / float(len(all_x1))
    avg_y1 = sum(all_y1) / float(len(all_y1))
    avg_x2 = sum(all_x2) / float(len(all_x2))
    avg_y2 = sum(all_y2) / float(len(all_y2))
    avg_slope = (avg_y2 - avg_y1) / (avg_x2 - avg_x1)

    print("avg all x1: ", avg_x1)
    print("avg all y1: ", avg_y1)
    print("avg all x2: ", avg_x2)
    print("avg all y2: ", avg_y2)
    print("avg slope (m): ", avg_slope)

    print("(min, max) x1: ", min(all_x1), max(all_x1))
    print("(min, max) x2: ", min(all_x2), max(all_x2))
    print("(min, max) y1: ", min(all_y1), max(all_y1))
    print("(min, max) y2: ", min(all_y2), max(all_y2))


    cv2.line(img, (min(all_x1), max(all_y1)), (max(all_x2), min(all_y2)), color, thickness)

    # draw right line
    all_x1 = []
    all_y1 = []
    all_x2 = []
    all_y2 = []
    all_slopes = []

    for x1, y1, x2, y2, angle in sides[1]:
        all_x1.append(x1)
        all_x2.append(x2)
        all_y1.append(y1)
        all_y2.append(y2)
        all_slopes.append((y2-y1)/(x2-x1))

    # cv2.line(img, (min(all_x1), min(all_y1)), (min(all_x2), max(all_y2)), color, thickness)
    # cv2.line(img, (649, 420), (728, 469), color, thickness)
    # cv2.line(img, (497, 326), (574, 372), color, thickness)

    x1 = min(all_x1)
    x2 = max(all_x2)
    y1 = min(all_y1)
    y2 = max(all_y2)

    avg_slope = sum(all_slopes)/len(all_slopes)
    max_y = img.shape[0]

    print('slope of line: ', avg_slope)
    print('x a y: ', max(all_x2))
    print('~x a y: ', (max(all_y2)/avg_slope))
    print('~x a max_y: ', max_y/avg_slope)

    cv2.line(img, (x1, y1), (x2, y2), color, thickness)
    # cv2.line(img, (x1, y1), (min(int(max_y/avg_slope), max(all_x2)), max_y), color, thickness)



def hough_lines(orig_img, img, rho, theta, threshold, min_line_len, max_line_gap):
    """
    `img` should be the output of a Canny transform.

    Returns an image with hough lines drawn.
    """
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len,
                            maxLineGap=max_line_gap)
    # line_img = np.zeros(img.shape, dtype=np.uint8)
    line_img = np.copy(orig_img) * 0  # creating a blank to draw lines on

    draw_lines(line_img, lines)
    return line_img


# Python 3 has support for cool math symbols.

def weighted_img(img, initial_img, α=0.8, β=1., λ=0.):
    """
    `img` is the output of the hough_lines(), An image with lines drawn on it.
    Should be a blank image (all black) with lines drawn on it.

    `initial_img` should be the image before any processing.

    The result image is computed as follows:

    initial_img * α + img * β + λ
    NOTE: initial_img and img must be the same shape!
    """
    return cv2.addWeighted(initial_img, α, img, β, λ)


#   START

def process_image(image):
    # printing out some stats and plotting
    # print('This image is:', type(image))
    # print('with dimesions:', image.shape)
    # print('width: ', image.shape[1])
    # print('height: ', image.shape[0])

    # plt.imshow(image)
    # plt.show()

    # call as plt.imshow(gray, cmap='gray') to show a grayscaled image
    gray = grayscale(image)
    # plt.imshow(gray, cmap='gray')
    # plt.show()

    # Define a kernel size for Gaussian smoothing / blurring
    kernel_size = 5  # Must be an odd number (3, 5, 7...)
    blur_gray = gaussian_noise(gray, kernel_size)

    # Define our parameters for Canny and run it
    low_threshold = 50
    high_threshold = 150
    edges = canny(blur_gray, low_threshold, high_threshold)

    # Display the image
    # plt.imshow(edges, cmap='Greys_r')
    # plt.show()


    # region mask

    # This time we are defining a four sided polygon to mask
    imshape = image.shape

    bottom_offset = 55
    img_height = imshape[0]
    img_width = imshape[1]

    # (W, H) == (x, y)
    vertices = np.array([
        [
            (bottom_offset, img_height),  # bottom left
            (img_width * 0.48, img_height * 0.60),  # top left
            (img_width * 0.54, img_height * 0.60),  # top right
            (img_width - bottom_offset, img_height)  # bottom right
        ]
    ], dtype=np.int32)

    # print('region of interest vertices: ', vertices)

    masked_edges = region_of_interest(edges, vertices)

    # Define the Hough transform parameters
    # Make a blank the same size as our image to draw on
    #
    # Defaults:
    # rho = 1
    # theta = np.pi/180
    # threshold = 1
    # min_line_length = 10
    # max_line_gap = 1

    rho = 2
    theta = np.pi / 180
    threshold = 40
    min_line_length = 20
    max_line_gap = 20

    result = hough_lines(image, masked_edges, rho, theta, threshold, min_line_length, max_line_gap)

    # Create a "color" binary image to combine with line image
    color_edges = np.dstack((edges, edges, edges))

    α = 0.35
    β = 0.8
    λ = 0.
    result = weighted_img(result, image, α, β, λ)
    # plt.imshow(result)
    # plt.show()

    return result


#
#   Test on Images
#
#   Now you should build your pipeline to work on the images in the directory "test_images"
#   You should make sure your pipeline works well on these images before you try the videos.
#


import os

for image_name in os.listdir("test_images/"):
    if image_name == '.DS_Store':
    # if image_name == '.DS_Store' or image_name != 'solidWhiteCurve.jpg':
    # if image_name == '.DS_Store' or image_name != 'solidYellowCurve.jpg':
    # if image_name == '.DS_Store' or image_name != 'horzLineTest.jpg':
        continue
    image = mpimg.imread('test_images/' + image_name)
    result = process_image(image)
    # plt.imshow(result)
    # plt.show()
    mpimg.imsave("RENDERED_" + image_name, result)

# Import everything needed to edit/save/watch video clips
from moviepy.editor import VideoFileClip
from IPython.display import HTML

# white_output = 'white.mp4'
# clip1 = VideoFileClip("solidWhiteRight.mp4")
# white_clip = clip1.fl_image(process_image)
# white_clip.write_videofile(white_output, audio=False)

# yellow_output = 'yellow.mp4'
# clip2 = VideoFileClip('solidYellowLeft.mp4')
# yellow_clip = clip2.fl_image(process_image)
# yellow_clip.write_videofile(yellow_output, audio=False)
