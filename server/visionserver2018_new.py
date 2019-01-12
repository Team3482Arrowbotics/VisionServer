#!/usr/bin/env python3

'''Vision server for 2018 Power Up -- updated to conform with VisionServer superclass'''

import cv2
import logging

from networktables.util import ntproperty
from networktables import NetworkTables

from visionserver import VisionServer
from switchtarget2018 import SwitchTarget2018
from cubefinder2018 import CubeFinder2018


class VisionServer2018_new(VisionServer):

    # Cube finding parameters

    # Color threshold values, in HSV space
    cube_hue_low_limit = ntproperty('/SmartDashboard/vision/cube/hue_low_limit', 25,
                                    doc='Hue low limit for thresholding (cube mode)')
    cube_hue_high_limit = ntproperty('/SmartDashboard/vision/cube/hue_high_limit', 75,
                                     doc='Hue high limit for thresholding (cube mode)')

    cube_saturation_low_limit = ntproperty('/SmartDashboard/vision/cube/saturation_low_limit', 95,
                                           doc='Saturation low limit for thresholding (cube mode)')
    cube_saturation_high_limit = ntproperty('/SmartDashboard/vision/cube/saturation_high_limit', 255,
                                            doc='Saturation high limit for thresholding (cube mode)')

    cube_value_low_limit = ntproperty('/SmartDashboard/vision/cube/value_low_limit', 95,
                                      doc='Value low limit for thresholding (cube mode)')
    cube_value_high_limit = ntproperty('/SmartDashboard/vision/cube/value_high_limit', 255,
                                       doc='Value high limit for thresholding (cube mode)')

    cube_exposure = ntproperty('/SmartDashboard/vision/cube/exposure', 0, doc='Camera exposure for cube (0=auto)')

    # Switch target parameters

    switch_hue_low_limit = ntproperty('/SmartDashboard/vision/switch/hue_low_limit', 70,
                                      doc='Hue low limit for thresholding (switch mode)')
    switch_hue_high_limit = ntproperty('/SmartDashboard/vision/switch/hue_high_limit', 100,
                                       doc='Hue high limit for thresholding (switch mode)')

    switch_saturation_low_limit = ntproperty('/SmartDashboard/vision/switch/saturation_low_limit', 100,
                                             doc='Saturation low limit for thresholding (switch mode)')
    switch_saturation_high_limit = ntproperty('/SmartDashboard/vision/switch/saturation_high_limit', 255,
                                              doc='Saturation high limit for thresholding (switch mode)')

    switch_value_low_limit = ntproperty('/SmartDashboard/vision/switch/value_low_limit', 130,
                                        doc='Value low limit for thresholding (switch mode)')
    switch_value_high_limit = ntproperty('/SmartDashboard/vision/switch/value_high_limit', 255,
                                         doc='Value high limit for thresholding (switch mode)')

    switch_exposure = ntproperty('/SmartDashboard/vision/switch/exposure', 6, doc='Camera exposure for switch (0=auto)')

    camera_height = ntproperty('/SmartDashboard/vision/camera_height', 23.0, doc='Camera height (inches)')

    def __init__(self, calib_file):
        super.__init__()

        # Initial mode for start of match.
        #  VisionServer switches to this mode after a second, to get the cameras initialized
        self.initial_mode = 'switch'

        self.switch_finder = SwitchTarget2018(calib_file)
        self.cube_finder = CubeFinder2018(calib_file)

        self.camera_device_vision = '/dev/v4l/by-id/usb-046d_Logitech_Webcam_C930e_DF7AF0BE-video-index0'
        self.camera_device_driver = '/dev/v4l/by-id/usb-046d_Logitech_Webcam_C930e_70E19A9E-video-index0'

        self.update_parameters()

        # Start in cube mode, then then switch to initial_mode after camera is fully initialized
        self.switch_mode('cube')

    @Override
    def update_parameters(self):
        '''Update processing parameters from NetworkTables values.
        Only do this on startup or if "tuning" is on, for efficiency'''

        # Make sure to add any additional created properties which should be changeable

        self.switch_finder.set_color_thresholds(self.switch_hue_low_limit, self.switch_hue_high_limit,
                                                self.switch_saturation_low_limit, self.switch_saturation_high_limit,
                                                self.switch_value_low_limit, self.switch_value_high_limit)
        self.cube_finder.set_color_thresholds(self.cube_hue_low_limit, self.cube_hue_high_limit,
                                              self.cube_saturation_low_limit, self.cube_saturation_high_limit,
                                              self.cube_value_low_limit, self.cube_value_high_limit)

        self.cube_finder.camera_height = self.camera_height
        return
    
    @Override
    def add_cameras(self):
        '''add a single camera at /dev/videoN, N=camera_device'''

        self.add_camera('intake', self.camera_device_vision, True)
        self.add_camera('driver', self.camera_device_driver, False)
        return

# syntax checkers don't like global variables, so use a simple function
def main():
    '''Main routine'''

    import argparse
    parser = argparse.ArgumentParser(description='2018 Vision Server')
    parser.add_argument('--test', action='store_true', help='Run in local test mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose. Turn up debug messages')
    parser.add_argument('--files', action='store_true', help='Process input files instead of camera')
    parser.add_argument('--calib', required=True, help='Calibration file for camera')
    parser.add_argument('input_files', nargs='*', help='input files')

    args = parser.parse_args()

    # To see messages from networktables, you must setup logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.test:
        # FOR TESTING, set this box as the server
        NetworkTables.enableVerboseLogging()
        NetworkTables.initialize()
    else:
        NetworkTables.initialize(server='10.28.77.2')

    server = VisionServer2018_new(args.calib)

    if args.files:
        if not args.input_files:
            parser.usage()

        server.run_files(args.input_files)
    else:
        server.run()
    return

# Main routine
if __name__ == '__main__':
    main()