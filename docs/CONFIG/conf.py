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
sys.path.insert(0, os.path.abspath('..'))
sys.path.append(os.path.abspath('../SegMeant'))
sys.path.append(os.path.abspath('../SegMeant/EngineSM'))
sys.path.append(os.path.abspath('../SegMeant/EngineSM/resources'))
sys.path.append(os.path.abspath('../SegMeant/EngineSM/tools'))
sys.path.append(os.path.abspath('../SegMeant/EngineSM/tree'))
sys.path.append(os.path.abspath('../SegMeant/EngineSM/statistics'))


project = 'SegMeant'
copyright = '2023, JeremdY'
author = 'JeremdY'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
    'sphinx.ext.viewcode', 'sphinx.ext.autosummary']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'fr'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

autodoc_default_flags = ['members']
autosummary_generate = True