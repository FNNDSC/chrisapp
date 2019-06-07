
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

        # create test directory where test files are created
        self.test_dir = os.path.dirname(__file__) + '/test'
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_add_argument(self):
        """
        Test whether add_argument method adds parameteres to the app
        """
        self.app.add_argument('--dir', dest='dir', type=str, default='./', optional=True,
                              help='look up directory', ui_exposed=True)
        self.app.add_argument('--flag', dest='flag', type=bool, default=False,
                              optional=True, help='a boolean flag', ui_exposed=True)
        # input and output dirs are predefined positional arguments so we moc them
        inputdir = "./"
        outputdir = "./"
        options = self.app.parse_args([inputdir, outputdir, '--flag'])
        self.assertEqual(options.dir, './')
        self.assertTrue(options.flag)

    def test_add_argument_raises_ValueError_if_optional_and_default_is_None(self):
        """
        Test whether add_argument method raises ValueError for an optional parameter
        with default set as None.
        """
        with self.assertRaises(ValueError):
            self.app.add_argument('--dir', dest='dir', type=str, default=None,
                                  optional=True, help='look up directory')

    def test_add_argument_raises_KeyError_if_optional_and_default_not_specified(self):
        """
        Test whether add_argument method raises KeyError for an optional parameter
        with default not specified.
        """
        with self.assertRaises(KeyError):
            self.app.add_argument('--dir', dest='dir', type=str, optional=True,
                                  help='look up directory')

    def test_add_argument_raises_KeyError_if_optional_descriptor_not_specified(self):
        """
        Test whether add_argument method raises KeyError if optional descriptor is
        not specified.
        """
        with self.assertRaises(KeyError):
            self.app.add_argument('--dir', dest='dir', type=str, help='look up directory')

    def test_add_argument_raises_ValueError_if_not_ui_exposed_and_not_optional(self):
        """
        Test whether add_argument method raises ValueError for a parameter that is not
        UI exposed and not optional.
        """
        with self.assertRaises(ValueError):
            self.app.add_argument('--dir', dest='dir', type=str, optional=False,
                                  help='look up directory', ui_exposed=False)

    def test_get_json_representation(self):
        """
        Test whether get_json_representation method returns an appropriate json object
        """
        repres = self.app.get_json_representation()
        self.assertEqual(repres['type'], self.app.TYPE)
        self.assertTrue('parameters' in repres)
        self.assertTrue('icon' in repres)
        self.assertTrue('authors' in repres)
        self.assertTrue('title' in repres)
        self.assertTrue('category' in repres)
        self.assertTrue('description' in repres)
        self.assertTrue('license' in repres)
        self.assertTrue('version' in repres)
        self.assertTrue('documentation' in repres)
        self.assertTrue('selfpath' in repres)
        self.assertTrue('selfexec' in repres)
        self.assertTrue('execshell' in repres)
        self.assertTrue('max_number_of_workers' in repres)
        self.assertTrue('max_memory_limit' in repres)
        self.assertTrue('max_cpu_limit' in repres)
        self.assertTrue('min_memory_limit' in repres)
        self.assertTrue('min_cpu_limit' in repres)
        self.assertTrue('min_gpu_limit' in repres)
        self.assertTrue('max_gpu_limit' in repres)

    def test_save_json_representation(self):
        """
        Test whether save_json_representation method saves the json representation object
        to an appropriate json file
        """
        outputdir = self.test_dir
        self.app.save_json_representation(outputdir)
        file_path = os.path.join(outputdir, self.app.__class__.__name__+ '.json')
        success = os.path.isfile(file_path)
        self.assertTrue(success)
        if success:
            with open(file_path) as json_file:
                repres = json.load(json_file)
                self.assertEqual(repres, self.app.get_json_representation())

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
        inputdir = "./"
        outputdir = self.test_dir
        self.app.options = self.app.parse_args([inputdir, outputdir])
        self.app.save_input_meta()
        success = os.path.isfile(os.path.join(outputdir, 'input.meta.json'))
        self.assertTrue(success)
        expected_input_meta_dict = {'json': False, 'meta': False, 'outputdir': outputdir,
                                    'saveinputmeta': False, 'inputmeta': None,
                                    'inputdir': inputdir, 'saveoutputmeta': False,
                                    'savejson': None, 'verbosity': '0', 'version': False,
                                    'man': False}
        if success:
            with open(os.path.join(outputdir, 'input.meta.json')) as meta_file:
                input_meta_dict = json.load(meta_file)
                self.assertEqual(input_meta_dict, expected_input_meta_dict)

    def test_save_output_meta(self):
        """
        Test save_output_meta method
        """
        inputdir = "./"
        outputdir = self.test_dir
        self.app.options = self.app.parse_args([inputdir, outputdir])
        self.app.save_output_meta()
        success = os.path.isfile(os.path.join(outputdir, 'output.meta.json'))
        self.assertTrue(success)
        if success:
            with open(os.path.join(outputdir, 'output.meta.json')) as meta_file:
                output_meta_dict = json.load(meta_file)
                self.assertEqual(output_meta_dict, self.app.OUTPUT_META_DICT)

    def test_load_output_meta(self):
        """
        Test load_output_meta method
        """
        inputdir = self.test_dir
        outputdir = self.test_dir
        self.app.options = self.app.parse_args([inputdir, outputdir])
        self.app.save_output_meta()
        output_meta_dict = self.app.load_output_meta()
        self.assertEqual(output_meta_dict, self.app.OUTPUT_META_DICT)
