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


class JsonAction(Action):
    """
    Custom action class to bypass required positional arguments when printing the app's
    JSON representation.
    """
    def __init__(self, *args, **kwargs):
        kwargs['nargs'] = 0
        Action.__init__(self, *args, **kwargs)

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
    SELFPATH = ''
    SELFEXEC = ''
    EXECSHELL = ''
    DESCRIPTION = ''
    DOCUMENTATION = ''
    LICENSE = ''
    VERSION = ''
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
        self.define_parameters()

    @staticmethod
    def path(string):
        """
        Define the 'path' data type that can be used by apps.
        """
        if not os.path.exists(string):
            msg = "Path %s not found!" % string
            raise ArgumentTypeError(msg)
        return string

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
                detail = "%s option required. " % e
                raise KeyError(detail)
            if optional and ('default' not in kwargs):
                detail = "A default value is required for optional parameters %s." % name
                raise KeyError(detail)

            # grab the default and help values
            default = None
            if 'default' in kwargs:
                default = kwargs['default']
            param_help = ""
            if 'help' in kwargs:
                param_help = kwargs['help']

            # set the ArgumentParser's action
            if param_type not in (str, int, float, bool, ChrisApp.path):
                detail = "unsupported type: '%s'" % param_type
                raise ValueError(detail)
            action = 'store'
            if param_type == bool:
                action = 'store_false' if default else 'store_true'
                del kwargs['default'] # 'default' and 'type' not allowed for boolean actions
                del kwargs['type']
            kwargs['action'] = action

            # store the parameters internally (param_type.__name__ to enable json serialization)
            param = {'name': name, 'type': param_type.__name__, 'optional': optional,
                     'flag': args[0], 'action': action, 'help': param_help, 'default': default}
            self._parameters.append(param)

            # add the parameter to the parser
            del kwargs['optional']
        ArgumentParser.add_argument(self, *args, **kwargs)

    def get_json_representation(self):
        """
        Return a JSON object with a representation of this app (type and parameters).
        """
        repres = {}
        repres['type'] = self.TYPE
        repres['parameters'] = self._parameters
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
        This method triggers the parsing of arguments. The run() method gets called
        if --json is not specified.
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

    def error(self, message):
        """
        The error handler if wrong commandline arguments are specified.
        """
        print()
        sys.stderr.write('ERROR: %s\n' % message)
        print()
        self.print_help()
        sys.exit(2)
