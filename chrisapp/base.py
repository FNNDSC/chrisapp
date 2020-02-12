"""
/**
 *
 *            sSSs   .S    S.    .S_sSSs     .S    sSSs
 *           d%%SP  .SS    SS.  .SS~YS%%b   .SS   d%%SP
 *          d%S'    S%S    S%S  S%S   `S%b  S%S  d%S'
 *          S%S     S%S    S%S  S%S    S%S  S%S  S%|
 *          S&S     S%S SSSS%S  S%S    d* S  S&S  S&S
 *          S&S     S&S  SSS&S  S&S   .S* S  S&S  Y&Ss
 *          S&S     S&S    S&S  S&S_sdSSS   S&S  `S&&S
 *          S&S     S&S    S&S  S&S~YSY%b   S&S    `S*S
 *          S*b     S*S    S*S  S*S   `S%b  S*S     l*S
 *          S*S.    S*S    S*S  S*S    S%S  S*S    .S*P
 *           SSSbs  S*S    S*S  S*S    S&S  S*S  sSS*S
 *            YSSP  SSS    S*S  S*S    SSS  S*S  YSS'
 *                         SP   SP          SP
 *                         Y    Y           Y
 *
 *                       U  L  T  R  O  N
 *
 * (c) 2016 Fetal-Neonatal Neuroimaging & Developmental Science Center
 *                   Boston Children's Hospital
 *
 *              http://childrenshospital.org/FNNDSC/
 *                        dev@babyMRI.org
 *
 */
"""
import sys
import os
from argparse import Action
from argparse import ArgumentParser
from argparse import ArgumentTypeError
import json


class NoArgAction(Action):
    """
    Base class for action classes that do not have arguments.
    """
    def __init__(self, *args, **kwargs):
        kwargs['nargs'] = 0
        Action.__init__(self, *args, **kwargs)


class JsonAction(NoArgAction):
    """
    Custom action class to bypass required positional arguments when printing the app's
    JSON representation.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        print(json.dumps(parser.get_json_representation()))
        parser.exit()


class SaveJsonAction(Action):
    """
    Custom action class to bypass required positional arguments when saving the app's JSON
    representation to a file.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        parser.save_json_representation(values)
        parser.exit()


class VersionAction(NoArgAction):
    """
    Custom action class to bypass required positional arguments when printing the app's
    version.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        print(parser.get_version())
        parser.exit()


class ManPageAction(NoArgAction):
    """
    Custom action class to bypass required positional arguments when showing the app's
    man page.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        parser.show_man_page()
        parser.exit()


class AppMetaDataAction(NoArgAction):
    """
    Custom action class to bypass required positional arguments when printing the app's
    meta data.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_app_meta_data()
        parser.exit()


class BaseClassAttrEnforcer(type):
    """
    Meta class to enforce class variables in subclasses.
    """
    def __init__(cls, name, bases, d):
        # class variables to be enforced in the subclasses
        attrs = ['DESCRIPTION', 'TYPE', 'TITLE', 'LICENSE', 'SELFPATH', 'SELFEXEC',
                 'EXECSHELL', 'OUTPUT_META_DICT', 'AUTHORS', 'VERSION']
        for attr in attrs:
            if attr not in d:
                raise ValueError("Class %s doesn't define %s class variable" % (name,
                                                                                attr))
        type.__init__(cls, name, bases, d)


class ChrisApp(ArgumentParser, metaclass=BaseClassAttrEnforcer):
    """
    The super class for all valid ChRIS plugin apps.
    """

    AUTHORS = 'FNNDSC (dev@babyMRI.org)'
    TITLE = ''
    CATEGORY = ''
    TYPE = 'ds'
    ICON = ''
    SELFPATH = ''
    SELFEXEC = ''
    EXECSHELL = ''
    DESCRIPTION = ''
    DOCUMENTATION = ''
    LICENSE = ''
    VERSION = ''
    MAX_NUMBER_OF_WORKERS = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS = 1  # Override with integer value
    MAX_CPU_LIMIT         = '' # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT         = '' # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT      = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT      = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_GPU_LIMIT         = 0  # Override with the minimum number of GPUs, as an integer, for your plugin
    MAX_GPU_LIMIT         = 0  # Override with the maximum number of GPUs, as an integer, for your plugin

    OUTPUT_META_DICT = {}

    def __init__(self):
        """
        The constructor of this app.
        """
        ArgumentParser.__init__(self, description=self.DESCRIPTION)
        # the custom parameter list
        self._parameters = []
        # operations on automatically computed JSON representation of the app
        ArgumentParser.add_argument(self, '--json', action=JsonAction, dest='json',
                                    default=False,
                                    help='show json representation of app and exit')
        ArgumentParser.add_argument(self, '--savejson', action=SaveJsonAction,
                                    type=ChrisApp.path, dest='savejson', metavar='DIR',
                                    help='save json representation file to DIR and exit')
        if self.TYPE == 'ds':
            # 'ds' plugins require an input directory
            ArgumentParser.add_argument(self, 'inputdir', action='store', type=str,
                              help='directory containing the input files')
        # all plugins require an output directory
        ArgumentParser.add_argument(self, 'outputdir', action='store', type=str,
                          help='directory containing the output files/folders')
        ArgumentParser.add_argument(self, '--inputmeta', action='store', dest='inputmeta',
                          help='meta data file containing the arguments passed to this app')
        ArgumentParser.add_argument(self, '--saveinputmeta', action='store_true',
                                    dest='saveinputmeta',
                                    help='save arguments to a JSON file')
        ArgumentParser.add_argument(self, '--saveoutputmeta', action='store_true',
                                    dest='saveoutputmeta',
                                    help='save output meta data to a JSON file')
        ArgumentParser.add_argument(self, '--version', action=VersionAction,
                                    dest='version', default=False,
                                    help='print app version and exit')
        ArgumentParser.add_argument(self, '--meta', action=AppMetaDataAction,
                                    dest='meta', default=False,
                                    help='print app meta data and exit')
        ArgumentParser.add_argument(self, '-v', '--verbosity', action='store', type=str,
                                    dest='verbosity', default="0",
                                    help='verbosity level for the app')
        ArgumentParser.add_argument(self, '--man', action=ManPageAction,
                                    dest='man', default=False,
                                    help="show the app's man page and exit")
        self.define_parameters()

    @staticmethod
    def path(string):
        """
        Define the 'path' data type that can be used by apps.
        It's a string representing a list of paths separated by commas.
        """
        path_list = [s.strip() for s in string.split(',')]
        for path in path_list:
            if not os.path.exists(path):
                raise ArgumentTypeError("Path %s not found!" % path)
        return ','.join(path_list)

    @staticmethod
    def unextpath(string):
        """
        Define the 'unextpath' data type that can be used by apps.
        It's a string representing a list of paths separated by commas. Unlike the
        'path' data type this type means that files won't be extracted from object
        storage.
        """
        path_list = [s.strip() for s in string.split(',')]
        return ','.join(path_list)

    def show_man_page(self):
        """
        Show the app's man page (abstract method in this class).
        """
        pass

    def define_parameters(self):
        """
        Define the parameters used by this app (abstract method in this class).
        """
        raise NotImplementedError("ChrisApp.define_parameters(self)")

    def run(self, options):
        """
        Execute this app (abstract method in this class).
        """
        raise NotImplementedError("ChrisApp.run(self, options)")

    def add_argument(self, *args, **kwargs):
        """
        Add a parameter to this app.
        """
        if not (('action' in kwargs) and (kwargs['action'] == 'help')):
            # make sure required parameter options were defined
            try:
                name = kwargs['dest']
                param_type = kwargs['type']
                optional = kwargs['optional']
            except KeyError as e:
                raise KeyError("%s option required." % e)
            if param_type not in (str, int, float, bool, ChrisApp.path,
                                  ChrisApp.unextpath):
                raise ValueError("Unsupported type: '%s'" % param_type)
            if optional:
                if param_type in (ChrisApp.path, ChrisApp.unextpath):
                    raise ValueError("Parameters of type 'path' or 'unextpath' cannot "
                                     "be optional.")
                if 'default' not in kwargs:
                    raise KeyError("A default value is required for optional parameter"
                                   " %s." % name)
                if kwargs['default'] is None:
                    raise ValueError("Default value cannot be 'None' for optional "
                                     "parameter %s." % name)
            # set the default, ui_exposed and help values
            default = kwargs['default'] if 'default' in kwargs else None
            param_help = kwargs['help'] if 'help' in kwargs else ""
            ui_exposed = kwargs['ui_exposed'] if 'ui_exposed' in kwargs else True
            if not ui_exposed and not optional:
                raise ValueError("Parameter %s is not optional and therefore must be "
                                 "exposed to the UI." % name)
            # set the ArgumentParser's action
            action = 'store'
            if param_type == bool:
                action = 'store_false' if default else 'store_true'
                # 'default' and 'type' options not allowed for boolean actions
                if 'default' in kwargs:
                    del kwargs['default']
                del kwargs['type']
            kwargs['action'] = action
            # store the parameters internally
            # use param_type.__name__ instead of param_type to enable json serialization
            param = {'name': name, 'type': param_type.__name__, 'optional': optional,
                     'flag': args[0], 'action': action, 'help': param_help,
                     'default': default, 'ui_exposed': ui_exposed}
            self._parameters.append(param)
            # remove custom options before calling superclass method
            del kwargs['optional']
            if 'ui_exposed' in kwargs:
                del kwargs['ui_exposed']
        ArgumentParser.add_argument(self, *args, **kwargs)

    def get_json_representation(self):
        """
        Return a JSON object with a representation of this app (type and parameters).
        """
        repres = {}
        repres['type'] = self.TYPE
        repres['parameters'] = self._parameters
        repres['icon'] = self.ICON
        repres['authors'] = self.AUTHORS
        repres['title'] = self.TITLE
        repres['category'] = self.CATEGORY
        repres['description'] = self.DESCRIPTION
        repres['documentation'] = self.DOCUMENTATION
        repres['license'] = self.LICENSE
        repres['version'] = self.VERSION
        repres['selfpath'] = self.SELFPATH
        repres['selfexec'] = self.SELFEXEC
        repres['execshell'] = self.EXECSHELL
        repres['max_number_of_workers'] = self.MAX_NUMBER_OF_WORKERS
        repres['min_number_of_workers'] = self.MIN_NUMBER_OF_WORKERS
        repres['max_memory_limit'] = self.MAX_MEMORY_LIMIT
        repres['max_cpu_limit'] = self.MAX_CPU_LIMIT 
        repres['min_memory_limit'] = self.MIN_MEMORY_LIMIT
        repres['min_cpu_limit'] = self.MIN_CPU_LIMIT 
        repres['min_gpu_limit'] = self.MIN_GPU_LIMIT
        repres['max_gpu_limit'] = self.MAX_GPU_LIMIT
        return repres

    def save_json_representation(self, dir_path):
        """
        Save the app's JSON representation object to a JSON file.
        """
        file_name = self.__class__.__name__+ '.json'
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'w') as outfile:
            json.dump(self.get_json_representation(), outfile)

    def launch(self, args=None):
        """
        This method triggers the parsing of arguments.
        """
        self.options = self.parse_args(args)
        if self.options.saveinputmeta:
            # save original input options
            self.save_input_meta()
        if self.options.inputmeta:
            # read new options from JSON file
            self.options = self.get_options_from_file(self.options.inputmeta)
        self.run(self.options)
        # if required save meta data for the output after running the plugin app
        if self.options.saveoutputmeta:
            self.save_output_meta()

    def get_options_from_file(self, file_path):
        """
        Return the options parsed from a JSON file.
        """
        # read options JSON file
        with open(file_path) as options_file:
            options_dict = json.load(options_file)
        options = []
        for opt_name in options_dict:
            options.append(opt_name)
            options.append(options_dict[opt_name])
        return self.parse_args(options)

    def save_input_meta(self):
        """
        Save the input meta data (options passed to the app) to a JSON file.
        """
        options = self.options
        file_path = os.path.join(options.outputdir, 'input.meta.json')
        with open(file_path, 'w') as outfile:
            json.dump(vars(options), outfile)

    def save_output_meta(self):
        """
        Save descriptive output meta data to a JSON file.
        """
        options = self.options
        file_path = os.path.join(options.outputdir, 'output.meta.json')
        with open(file_path, 'w') as outfile:
            json.dump(self.OUTPUT_META_DICT, outfile)

    def load_output_meta(self):
        """
        Load descriptive output meta data from a JSON file in the input directory.
        """
        options = self.options
        file_path = os.path.join(options.inputdir, 'output.meta.json')
        with open(file_path) as infile:
            return json.load(infile)

    def get_version(self):
        """
        Return the app's version.
        """
        return self.VERSION

    def print_app_meta_data(self):
        """
        Print the app's meta data.
        """
        l_metaData  = dir(self)
        l_classVar  = [x for x in l_metaData if x.isupper() ]
        for str_var in l_classVar:
            str_val = getattr(self, str_var)
            print("%20s: %s" % (str_var, str_val))

    def error(self, message):
        """
        The error handler if wrong commandline arguments are specified.
        """
        print()
        sys.stderr.write('ERROR: %s\n' % message)
        print()
        self.print_help()
        sys.exit(2)
