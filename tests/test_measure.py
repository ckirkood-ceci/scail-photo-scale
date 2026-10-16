"""Offline synthetic geometry checks; NOT a real camera accuracy evaluation."""
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'measure.py'


def run(*args):
    res = subprocess.run([sys.executable, *[str(x) for x in args]],
                         capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


class PhotoScaleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()

    def test_manual_rectangle_homography(self):
        img = np.ones((900, 1000, 3), dtype=np.uint8) * 240
        pic = self.path/'image.png'; cv2.imwrite(str(pic), img)
        plane = np.float32([[0, 0], [100, 0], [100, 80], [0, 80]])
        pixel = np.float32([[105, 150], [815, 200], [765, 710], [80, 660]])
        H = cv2.getPerspectiveTransform(plane,pixel)
        ref = cv2.perspectiveTransform(np.float32([[5, 5], [65, 5], [65, 45], [5, 45]]).reshape(-1,1,2),H).reshape(-1,2)
        target = cv2.perspectiveTransform(np.float32([[10, 70], [70, 70]]).reshape(-1,1,2),H).reshape(-1,2)
        pts = lambda xs: ';'.join(','.join(f'{v:.5f}' for v in row) for row in xs)
        out=run(SCRIPT,pic,'--reference','rectangle','--size-mm','60,40', '--quad',pts(ref), '--segment',pts(target),'--annotated', self.path/'annotated.png')
        self.assertAlmostEqual(out['distance_mm'],60,delta=.02)
        self.assertTrue((self.path/'annotated.png').exists())

    def test_marker_detection(self):
        mark=cv2.aruco.generateImageMarker(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50),23,300)
        canvas=np.ones((650,700),dtype=np.uint8)*255
        canvas[150:450, 200:500]=mark
        path=self.path/'marker.png';cv2.imwrite(str(path),canvas)
        out=run(SCRIPT,path,'--reference','marker','--segment','210,230;410,230')
        self.assertAlmostEqual(out['distance_mm'],20,delta=.2)

    def test_circle_simple_scale(self):
        path=self.path/'blank.png'; cv2.imwrite(str(path),np.zeros((900,900,3),dtype=np.uint8))
        out=run(SCRIPT,path,'--reference','circle','--preset','us-quarter', '--diameter-px','100,200;342.6,200', '--segment','100,600;600,600')
        self.assertAlmostEqual(out['distance_mm'],50,delta=.02)
        self.assertEqual(out['mode'],'simple_scale_no_perspective_correction')

    def test_custom_profile_and_guided_pattern(self):
        profile=self.path/'wallet.json'
        subprocess.run([sys.executable,str(ROOT/'scripts'/'create_profile.py'),'--name','Test Card','--width-mm','88','--height-mm','56','--output',str(profile)],check=True,capture_output=True,text=True)
        self.assertEqual(json.loads(profile.read_text())['width_mm'],88)
        p=run(ROOT/'scripts'/'pattern_guide.py','--surface-width-mm','85','--surface-height-mm','54','--grid-mm','5')
        self.assertEqual(p['reference_rectangle_mm'],[75,40])
        self.assertIn('NOT automatically',p['warning'])
        pic=self.path/'blank.png'; cv2.imwrite(str(pic),np.zeros((300,500,3),dtype=np.uint8))
        r=run(SCRIPT,pic,'--reference','rectangle','--profile',profile,'--quad','20,20;460,20;460,300;20,300','--segment','20,20;460,20')
        self.assertAlmostEqual(r['distance_mm'],88,delta=.03)


if __name__ == '__main__':unittest.main()
