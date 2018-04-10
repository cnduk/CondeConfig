from collections import Mapping
from glob import glob
import json
from os.path import basename, splitext
from keyword import iskeyword

import six

# map of <namespace tuple>: (_Config(), config_dict)
# Used by the _Config items to look up their values
_NAMESPACES = {}
# map of _Config(): (config_dict, <namespace tuple>)
_OBJECTS = {}

__ALL__ = [
    'config',
    'config_init',
    'config_init_from_file',
    'config_into',
    'config_into_from_file',
    'config_set',
]


class _Config(Mapping):
    # The Following method definitions __getitem__, __iter__ and __len__
    # are required as a subclass of Mapping
    def __getitem__(self, key):
        # This is required by collections.Mapping
        return self._config_items[key]

    def __iter__(self):
        # Through this, collections.Mapping can use __getitem__ to fulfil
        # items(), values(), and keys() (and their iter* counterparts
        # in python 2.x)
        return iter(self._config_items)

    def __len__(self):
        return len(self._config_items)

    # This is overridden by Mapping, so let's just put it back
    def __hash__(self):
        return id(self)

    def __getattr__(self, name):
        # Because self._namespaces is set in the objects dict,
        # __getattr__ is not called when accessing self._namespaces
        try:
            return _NAMESPACES[self._namespace + (name,)][0]

        except KeyError:
            raise AttributeError("attribute value not set {}".format(name))

    def __setattr__(self, name, val):
        raise AttributeError("item assignment not supported")

    def __repr__(self):
        return '<{} ns={}>'.format(self.__class__.__name__, self._namespace)

    @property
    def _config_items(self):
        return _OBJECTS[self][0]

    @property
    def _namespace(self):
        return _OBJECTS[self][1]

    def get(self, key, default=None):
        return self._config_items.get(key, default)

    def get_namespaces(self):
        """Returns a dict of namespace*:_Config() for configs in one namespace
            below the given namespace.

            *namespace releated to this current config
        """
        return {
            namespace[-1]: config
            for namespace, (config, _)
            in _NAMESPACES.items()
            if len(self._namespace)+1 == len(namespace)
            and self._namespace == namespace[:-1]
        }


def _create_namespace(namespace):
    msg = None
    for word in namespace:
        if not all(char.isalnum() or char=='_' for char in word):
            msg = "namespace words can only contain alphanumeric " \
                    "characters or underscores."

        elif iskeyword(word):
            msg = "namespaces can't contain keywords."

        elif word.startswith('_'):
            msg = "Namespaces can't contain words starting with an underscore."

        elif word[0].isdigit():
            msg = "Namespaces can't contain words starting with a number."

        if msg:
            raise ValueError(
                    msg + " found \"{}\" in {}".format(word, namespace))

    new_items = {}
    new_cfg = _Config()
    _OBJECTS[new_cfg] = (new_items, namespace)
    _NAMESPACES[namespace] = (new_cfg, new_items)


def _load_json(filename):
    with open(filename) as json_file:
        return json.load(json_file)


def get_config(namespace):
    """Gets the config object based on the namespace

    Args:
        namespace (tuple): strings representing namespace keys

    Returns:
        tuple: _Config, dict of items
    """
    assert isinstance(namespace, tuple)
    assert all(isinstance(i, six.string_types) for i in namespace)

    if namespace not in _NAMESPACES:
        # ()
        if len(namespace) == 0:
            _create_namespace(namespace)

        # ('some', 'actual', 'items')
        else:
            for index, _ in enumerate(namespace):
                current_namespace = namespace[:index+1]

                if current_namespace not in _NAMESPACES:
                    _create_namespace(current_namespace)


    return _NAMESPACES[namespace]


def config_init(data):
    """Updates config with the data

    Args:
        data (dict): the data
    """
    _, items = get_config(())
    items.update(data)


def config_init_from_file(filename):
    """Updates the config with data provided from a file

    Args:
        filename (string): location of json file
    """
    for a_filename in glob(filename):
        json_data = _load_json(a_filename)
        _, items = get_config(())
        items.update(json_data)


def config_into(data, namespace):
    """Updates the config with the data but into a namespace

    Args:
        data (dict): the data
        namespace (string): namespace
    """
    namespace_tuple = tuple(namespace.split('.'))
    _, items = get_config(namespace_tuple)
    items.update(data)


def config_into_from_file(filename, namespace):
    """Updates the config with the data from a file but into a namespace

    Args:
        filename (string): location of json file
        namespace (string): namespace
    """
    for a_filename in glob(filename):
        namespace_key = splitext(basename(a_filename))[0]
        json_data = _load_json(a_filename)
        config_into(json_data, '{}.{}'.format(namespace, namespace_key))


def config_set(key, value, namespace=None):
    """Sets a key, value into config unlesss a namespace is specified

    Args:
        key (string): key
        value (string): value
        namespace (None, optional): tuple of strings
    """
    if namespace:
        namespace_tuple = tuple(namespace.split('.'))
    else:
        namespace_tuple = ()

    _, items = get_config(namespace_tuple)
    items[key] = value


config = get_config(())[0]
