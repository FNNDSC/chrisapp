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
 * (c) 2016-2021 Fetal-Neonatal Neuroimaging & Developmental Science Center
 *                   Boston Children's Hospital
 *
 *              http://childrenshospital.org/FNNDSC/
 *                        dev@babyMRI.org
 *
 */
"""
import os
import sys
from argparse import Action, ArgumentParser, ArgumentTypeError
import json
import importlib.metadata


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
        if 'PACKAGE' in d:
            # interrogate setup.py to automatically fill in some
            # class attributes for the subclass
            autofill = ['AUTHORS', 'TITLE', 'DESCRIPTION', 'LICENSE', 'DOCUMENTATION',
                        'VERSION']
            for attr in autofill:
                if attr in d:
                    raise ValueError(
                        'Do not manually set value value for '
                        f'"{attr}" when "PACKAGE={d["PACKAGE"]}" is declared')

            pkg = importlib.metadata.Distribution.from_name(d['PACKAGE'])
            setup = pkg.metadata
            cls.AUTHORS = f'{setup["author"]} <{setup["author-email"]}>'
            d['AUTHORS'] = cls.AUTHORS
            cls.TITLE = setup['name']
            d['TITLE'] = cls.TITLE
            cls.DESCRIPTION = setup['summary']
            d['DESCRIPTION'] = cls.DESCRIPTION
            cls.LICENSE = setup['license']
            d['LICENSE'] = cls.LICENSE
            cls.DOCUMENTATION = setup['home-page']
            d['DOCUMENTATION'] = cls.DOCUMENTATION
            cls.VERSION = setup['version']
            d['VERSION'] = cls.VERSION

            if 'SELFEXEC' not in d:
                eps = [ep for ep in pkg.entry_points if ep.group == 'console_scripts']
                if eps:
                    if len(eps) > 1:
                        # multiple console_scripts found but maybe
                        # they're just the same thing
                        different_scripts = [ep for ep in eps if ep.value != eps[0].value]
                        if different_scripts:
                            raise ValueError(
                                'SELFEXEC not defined and more than one '
                                'console_scripts found')
                    cls.SELFEXEC = eps[0].name
                    d['SELFEXEC'] = cls.SELFEXEC
                    cls.EXECSHELL = sys.executable
                    d['EXECSHELL'] = cls.EXECSHELL
                    # when pip is used to install a script on the metal, it is put in
                    # /usr/local/bin but if we're in a virtualenv, try to detect that
                    cls.SELFPATH = os.path.join(os.getenv('VIRTUAL_ENV'), 'bin') \
                        if 'VIRTUAL_ENV' in os.environ else '/usr/local/bin'
                    d['SELFPATH'] = cls.SELFPATH

        # class variables to be enforced in the subclasses
        attrs = [
            'DESCRIPTION', 'TYPE', 'TITLE', 'LICENSE', 'AUTHORS', 'VERSION',
            'SELFPATH', 'SELFEXEC', 'EXECSHELL'
        ]
        for attr in attrs:
            if attr not in d:
                raise ValueError(f"Class {name} doesn't define {attr} class variable")
            if type(d[attr]) is not str:
                raise ValueError(f'{attr} ({type(attr)}) must be a string')
        if 'OUTPUT_META_DICT' not in d:
            raise ValueError(f"Class {name} doesn't define OUTPUT_META_DICT")
        if type(d['OUTPUT_META_DICT']) is not dict:
            raise ValueError('OUTPUT_META_DICT must be dict')
        type.__init__(cls, name, bases, d)


class ChrisApp(ArgumentParser, metaclass=BaseClassAttrEnforcer):
    """
    The superclass for all ChRIS plugin apps.

    Meta-information about the subclass must be given as class attributes.
    This is enforced by a metaclass.

    Subclasses should manually define

        AUTHORS, TITLE, DESCRIPTION, LICENSE, DOCUMENTATION, VERSION,
        SELFPATH, SELFEXEC, EXECSHELL

    Or, the metaclass can interrogate setup.py to discover the information
    automatically. Enable this feature by setting

        PACKAGE = __package__

    The following class variables *must* be supplied, as they cannot
    be discovered from setup.py

        TYPE, OUTPUT_META_DICT

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
    MAX_NUMBER_OF_WORKERS = 1
    """Integer value"""
    MIN_NUMBER_OF_WORKERS = 1
    """Integer value"""
    MAX_CPU_LIMIT = ''
    """millicore value as string, e.g. '2000m'"""
    MIN_CPU_LIMIT = ''
    """millicore value as string, e.g. '2000m'"""
    MAX_MEMORY_LIMIT = ''
    """string, e.g. '1Gi', '2000Mi'"""
    MIN_MEMORY_LIMIT = ''
    """string, e.g. '1Gi', '2000Mi'"""
    MIN_GPU_LIMIT = 0
    """number of GPUs"""
    MAX_GPU_LIMIT = 0
    """number of GPUs"""

    OUTPUT_META_DICT = {}

    def __init__(self):
        """
        The constructor of this app.
        """
        ArgumentParser.__init__(self, description=self.DESCRIPTION)

        # the custom parameter list
        self._parameters = []

        ArgumentParser.add_argument(self, '--json', action=JsonAction, dest='json',
                                    default=False,
                                    help='show json representation of app and exit')
        ArgumentParser.add_argument(self, '--savejson', action=SaveJsonAction,
                                    type=ChrisApp.path, dest='savejson', metavar='DIR',
                                    help='save json representation file to DIR and exit')

        ArgumentParser.add_argument(self, '--inputmeta', action='store', dest='inputmeta',
                                    help='meta data file containing the arguments passed '
                                         'to this app')
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

        # 'ds' plugins require an input directory positional argument
        if self.TYPE == 'ds':
            ArgumentParser.add_argument(self, 'inputdir', action='store', type=str,
                                        help='directory containing the input files')

        # all plugins require an output directory positional argument
        ArgumentParser.add_argument(self, 'outputdir', action='store', type=str,
                                    help='directory containing the output files/folders')

        # topological plugin's especial parameters
        if self.TYPE == 'ts':
            self.add_argument('--plugininstances', dest='plugininstances', type=str,
                              optional=True, default='',
                              help='string representing a comma-separated list of plugin '
                                   'instance ids')
            self.add_argument('-f', '--filter', dest='filter', type=str, optional=True,
                              default='',
                              help="regular expression to filter the plugin instances' "
                                   "output path")
            self.add_argument('-e', '--extractpaths', dest='extractpaths', type=bool,
                              optional=True, default=False,
                              help="if set then the matched paths from the plugin "
                                   "instances' output path are sent to the remote "
                                   "compute")
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
        Overriden to add a new parameter to this app.
        """
        if not (('action' in kwargs) and (kwargs['action'] == 'help')):
            self.validate_argument_options(**kwargs)

            # set required, default, ui_exposed and help values
            optional = kwargs['optional']
            if 'required' not in kwargs:
                kwargs['required'] = not optional
            default = kwargs['default'] if 'default' in kwargs else None
            param_help = kwargs['help'] if 'help' in kwargs else ''
            ui_exposed = kwargs['ui_exposed'] if 'ui_exposed' in kwargs else True

            # set the ArgumentParser's action
            param_type = kwargs['type']
            action = 'store'
            if param_type == bool:
                action = 'store_false' if default else 'store_true'
                # 'default' and 'type' options not allowed for boolean actions
                if 'default' in kwargs:
                    del kwargs['default']
                del kwargs['type']
            kwargs['action'] = action

            # set the flag
            short_flag = flag = args[0]
            if len(args) > 1:
                if args[0].startswith('--'):
                    short_flag = args[1]
                else:
                    flag = args[1]

            # store the parameter internally
            # use param_type.__name__ instead of param_type to enable json serialization
            name = kwargs['dest']
            param = {'name': name, 'type': param_type.__name__, 'optional': optional,
                     'flag': flag, 'short_flag': short_flag, 'action': action,
                     'help': param_help, 'default': default, 'ui_exposed': ui_exposed}
            self._parameters.append(param)

            # remove custom options before calling superclass method
            del kwargs['optional']
            if 'ui_exposed' in kwargs:
                del kwargs['ui_exposed']
        ArgumentParser.add_argument(self, *args, **kwargs)

    def validate_argument_options(self, **kwargs):
        """
        Validate argument's options passed as kwargs.
        """
        # make sure required parameter options are defined
        try:
            name = kwargs['dest']
            optional = kwargs['optional']
            param_type = kwargs['type']
        except KeyError as e:
            raise KeyError("%s option required." % e)

        # 'optional' (our custom flag) and 'required' (from argparse) should agree
        if ('required' in kwargs) and (kwargs['required'] == optional):
            raise KeyError("Values for 'required' and 'optional' contradict for "
                           "parameter %s." % name)

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

        ui_exposed = kwargs['ui_exposed'] if 'ui_exposed' in kwargs else True
        if not ui_exposed and not optional:
            raise ValueError("Parameter %s is not optional and therefore must be "
                             "exposed to the UI." % name)

    def get_json_representation(self):
        """
        Return a JSON object with a representation of this app (type and parameters).
        """
        representation = {'type': self.TYPE,
                          'parameters': self._parameters,
                          'icon': self.ICON,
                          'authors': self.AUTHORS,
                          'title': self.TITLE,
                          'category': self.CATEGORY,
                          'description': self.DESCRIPTION,
                          'documentation': self.DOCUMENTATION,
                          'license': self.LICENSE,
                          'version': self.VERSION,
                          'selfpath': self.SELFPATH,
                          'selfexec': self.SELFEXEC,
                          'execshell': self.EXECSHELL,
                          'max_number_of_workers': self.MAX_NUMBER_OF_WORKERS,
                          'min_number_of_workers': self.MIN_NUMBER_OF_WORKERS,
                          'max_memory_limit': self.MAX_MEMORY_LIMIT,
                          'min_memory_limit': self.MIN_MEMORY_LIMIT,
                          'max_cpu_limit': self.MAX_CPU_LIMIT,
                          'min_cpu_limit': self.MIN_CPU_LIMIT,
                          'max_gpu_limit':self.MAX_GPU_LIMIT,
                          'min_gpu_limit': self.MIN_GPU_LIMIT
                          }
        return representation

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
        Trigger the parsing of arguments.
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
        meta_data = dir(self)
        class_var = [x for x in meta_data if x.isupper()]
        for str_var in class_var:
            str_val = getattr(self, str_var)
            print("%20s: %s" % (str_var, str_val))
