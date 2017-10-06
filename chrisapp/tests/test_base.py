
import os
import shutil
import json
import unittest

from chrisapp.base import ChrisApp


def define_parameters(self):
    pass

class ChrisAppTests(unittest.TestCase):

    def setUp(self):
        # override abstract define_parameters method
        ChrisApp.define_parameters = define_parameters
        self.app = ChrisApp()

    def test_add_argument(self):
        """
        Test whether add_argument method adds parameteres to the app
        """
        self.app.add_argument('--dir', dest='dir', type=str, default='./', optional=True,
                              help='look up directory')
        self.app.add_argument('--flag', dest='flag', type=bool, default=False, optional=True,
                              help='a boolean flag')
        # input and output dirs are predefined positional arguments so we moc them
        inputdir = "./"
        outputdir = "./"
        options = self.app.parse_args([inputdir, outputdir, '--flag'])
        self.assertEqual(options.dir, './')
        self.assertTrue(options.flag)

    def test_get_json_representation(self):
        """
        Test whether get_json_representation method returns an appropriate json object
        """
        repres = self.app.get_json_representation()
        self.assertEqual(repres['type'], self.app.TYPE)
        self.assertTrue('parameters' in repres)

    def test_launch(self):
        """
        Test launch method
        """
        # input and output dirs are predefined positional arguments so we moc them
        inputdir = "./"
        outputdir = "./"
        success = False
        try:
            self.app.launch([inputdir, outputdir])
        except NotImplementedError:
            success = True
        self.assertTrue(success)

    def test_save_input_meta(self):
        """
        Test save_input_meta method
        """
        # create test directory where files are created
        test_dir = os.path.dirname(__file__) + '/test'
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        inputdir = "./"
        outputdir = "./"
        options = self.app.parse_args([inputdir, outputdir])
        self.app.save_input_meta(options)
        success = os.path.isfile(os.path.join(inputdir, 'input.meta.json'))
        self.assertTrue(success)
        expected_options_dir = {'json': False, 'outputdir': './', 'saveinputmeta': False,
                                'inputmeta': None, 'inputdir': './', 'saveoutputmeta': False}
        if success:
            with open(os.path.join(inputdir, 'input.meta.json')) as options_file:
                options_dict = json.load(options_file)
                self.assertEqual(options_dict, expected_options_dir)
            shutil.rmtree(test_dir)
