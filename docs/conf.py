# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# OS path commands should be uncommented in conf.py file
# so that html utility could access the right project files to 
# generate documentation. 
import os
import sys



sys.path.insert(0, os.path.abspath('../scripts/python'))
#sys.path.insert(0, os.path.abspath('../SegMeant'))
"""sys.path.append(os.path.abspath('../SegMeant/EngineSM'))
sys.path.append(os.path.abspath('../SegMeant/EngineSM/resources'))
sys.path.append(os.path.abspath('../SegMeant/EngineSM/tools'))
sys.path.append(os.path.abspath('../SegMeant/EngineSM/tree'))
sys.path.append(os.path.abspath('../SegMeant/EngineSM/statistics'))"""


project = 'SegMeant'
copyright = '2023, JeremdY'
author = 'JeremdY'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
    'sphinx.ext.viewcode', 'sphinx.ext.autosummary', 
    'sphinx.ext.inheritance_diagram', 'sphinx.ext.graphviz']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'fr'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autodoc_default_options = {"members": True, "undoc-members": True, "private-members": True}
autosummary_generate = True

plantuml = 'java -jar plantuml.jar'

inheritance_graph_attrs = dict(rankdir="TB", size='""')

sphinx_pyreverse_output = 'png'
sphinx_pyreverse_filter_mode = 'ALL'
#sphinx_pyreverse_module_names = "y"
sphinx_pyreverse_show_builtin = False
sphinx_pyreverse_all_associated = True
sphinx_pyreverse_all_ancestors = True
sphinx_pyreverse_only_classnames = False