from glob import glob
import json
import six

_NAMESPACES = {}
_OBJECTS = {}

__ALL__ = [
    'config',
    'config_init',
    'config_init_from_file',
    'config_into',
    'config_into_from_file',
    'config_set',
]

class _Config(object):

    def __getattr__(self, name):
        # Because self._namespaces is set in the objects dict,
        # __getattr__ is not called when accessing self._namespaces
        try:
            return _NAMESPACES[self._namespace + (name,)][0]

        except KeyError:
            raise AttributeError("attribute value not set {}".format(name))

    def __getitem__(self, key):
        # Could catch and raise specific error here.
        return self._config_items[key]

    def __repr__(self):
        return '<{} ns={}>'.format(self.__class__.__name__, self._namespace)

    def __setattr__(self, name, val):
        raise AttributeError("item assignment not supported")

    def __setitem__(self, *args):
        raise Exception("cannot set items")

    @property
    def _config_items(self):
        return _OBJECTS[self][0]

    @property
    def _namespace(self):
        return _OBJECTS[self][1]

    def get(self, *args, **kwargs):
        """Gets a value from the config

        Args:
            *args (list): list of arguments
            **kwargs (dict): dict of keyword args

        Returns:
            any: the value
        """
        return self._config_items.get(*args, **kwargs)


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

    # e.g. namespace = ('config', 'brand', 'vogue')
    if namespace not in _NAMESPACES:
        new_items = {}
        new_cfg = _Config()
        _OBJECTS[new_cfg] = (new_items, namespace)
        _NAMESPACES[namespace] = (new_cfg, new_items)

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
        json_data = _load_json(a_filename)
        config_into(json_data, namespace)


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
