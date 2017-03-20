#importing some useful packages
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import os
import cv2
import imageio
imageio.plugins.ffmpeg.download()
from moviepy.editor import VideoFileClip


def grayscale(img):
    """Applies the Grayscale transform
    This will return an image with only one color channel
    but NOTE: to see the returned image as grayscale
    (assuming your grayscaled image is called 'gray')
    you should call plt.imshow(gray, cmap='gray')"""
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # Or use BGR2GRAY if you read an image with cv2.imread()
    # return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def canny(img, low_threshold, high_threshold):
    """Applies the Canny transform"""
    return cv2.Canny(img, low_threshold, high_threshold)


def gaussian_blur(img, kernel_size):
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


def get_line_eqn(x1, y1, x2, y2):
    m = (y2-y1)/(x2-x1)
    b = y1 - m*x1
    return m, b

def draw_lines(img, lines, vertical_limits, color=(255, 0, 0), thickness=2):
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

    # Group similar lines
    left_lane_lines = []
    right_lane_lines = []

    for line in lines:
        line = line[0]
        if get_line_eqn(*line)[0] > 0:
            left_lane_lines.append(line)
        else:
            right_lane_lines.append(line)

    # Average similar lines
    lane_lines = []
    if left_lane_lines:
        avg_left_lane_lines = np.mean(left_lane_lines, axis=0, dtype=int)
        lane_lines.append(avg_left_lane_lines)
    if right_lane_lines:
        avg_right_lane_lines = np.mean(right_lane_lines, axis=0, dtype=int)
        lane_lines.append(avg_right_lane_lines)

    # Extrapolate similar line
    extrapolated_lines = []
    y1, y2 = vertical_limits
    for lane_line in lane_lines:
        m, b = get_line_eqn(*lane_line)
        x1 = (y1 - b) / m
        x2 = (y2 - b) / m
        extrapolated_lines.append(np.array([x1, y1, x2, y2], dtype=int))

    for line in extrapolated_lines:
        x1, y1, x2, y2 = line
        cv2.line(img, (x1, y1), (x2, y2), color, thickness)


def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap, vertical_limits):
    """
    `img` should be the output of a Canny transform.

    Returns an image with hough lines drawn.
    """
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len,
                            maxLineGap=max_line_gap)
    line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    draw_lines(line_img, lines, vertical_limits)
    return line_img


def weighted_img(img, initial_img, alpha=0.8, beta=1., gamma=0.):
    """
    `img` is the output of the hough_lines(), An image with lines drawn on it.
    Should be a blank image (all black) with lines drawn on it.

    `initial_img` should be the image before any processing.

    The result image is computed as follows:

    initial_img * α + img * β + λ
    NOTE: initial_img and img must be the same shape!
    """
    return cv2.addWeighted(initial_img, alpha, img, beta, gamma)


def lane_finding(raw_image):

    # Grayscale the image
    image = grayscale(raw_image)

    # Apply Gaussian blur
    image = gaussian_blur(image, 5)

    # Apply Canny filter
    image = canny(image, 50, 150)

    # Crop up the region of interest
    image_height, image_width = image.shape
    top_left = (0.46*image_width, 0.60*image_height)
    top_right = (0.51*image_width, 0.60*image_height)
    bottom_left = (0*image_width, image_height)
    bottom_right = (image_width, image_height)
    vertices = np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
    image = region_of_interest(image, vertices)

    # Apply Hough Transform to get lanes
    rho = 2  # distance resolution in pixels of the Hough grid
    theta = np.pi * 1 / 180  # angular resolution in radians of the Hough grid
    threshold = 50  # minimum number of votes (intersections in Hough grid cell)
    min_line_length = 60  # minimum number of pixels making up a line
    max_line_gap = 50  # maximum gap in pixels between connectable line segments
    image = hough_lines(image, rho, theta, threshold, min_line_length, max_line_gap,
                        vertical_limits=(bottom_left[1], top_left[1]))

    return image

def process_image(image):
    annotated_image = lane_finding(image)
    overlay_image = weighted_img(annotated_image, image, alpha=0.3, beta=1.0, gamma=0.2)
    return overlay_image


if __name__ == "__main__":

    # First, annotate images
    test_image_files_dir = os.path.join(os.getcwd(), "test_images")
    annotated_image_files_dir = os.path.join(os.getcwd(), "test_images_output")
    if not os.path.exists(annotated_image_files_dir):
        os.makedirs(annotated_image_files_dir)
    raw_image_files = os.listdir(test_image_files_dir)

    for raw_image_file in raw_image_files:
        raw_image_full_path = os.path.join(test_image_files_dir, raw_image_file)
        annotated_image_full_path = os.path.join(annotated_image_files_dir, raw_image_file)

        raw_image = mpimg.imread(raw_image_full_path)
        annotated_image = lane_finding(raw_image)

        # Overlay the identified lanes on the original image
        overlay_image = weighted_img(annotated_image, raw_image, alpha=0.3, beta=1.0, gamma=0.2)
        plt.imshow(overlay_image)
        plt.savefig(annotated_image_full_path, bbox_inches="tight", frameon=False)

    # Second, annotate videos
    test_video_files_dir = os.path.join(os.getcwd(), "test_videos")
    annotated_video_files_dir = os.path.join(os.getcwd(), "test_videos_output")
    if not os.path.exists(annotated_video_files_dir):
        os.makedirs(annotated_video_files_dir)
    raw_video_files = os.listdir(test_video_files_dir)

    for raw_video_file in raw_video_files:
        raw_video_full_path = os.path.join(test_video_files_dir, raw_video_file)
        annotated_video_full_path = os.path.join(annotated_video_files_dir, raw_video_file)

        raw_video = VideoFileClip(raw_video_full_path)
        annotated_video = raw_video.fl_image(process_image)
        annotated_video.write_videofile(annotated_video_full_path, audio=False)
