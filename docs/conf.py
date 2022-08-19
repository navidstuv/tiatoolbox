#!/usr/bin/env python
# flake8: noqa
#
# tiatoolbox documentation build configuration file, created by
# sphinx-quickstart on Fri Jun  9 13:47:02 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# auto generated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory is
# relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
#
import os
import pathlib
import shutil
import sys

sys.path.insert(0, os.path.abspath(".."))

import tiatoolbox  # noqa: E402

# -- General configuration ---------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# requires sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",  # Create neat summary tables
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx_toolbox.collapse",
    "recommonmark",
    "nbsphinx",
    "sphinx_gallery.load_style",
]

autosummary_generate = True  # Turn on sphinx.ext.autosummary
autoclass_content = "both"  # Add __init__ doc (ie. params) to class summaries
# Remove 'view source code' from top of page (for html, not python)
html_show_sourcelink = False
# If no docstring, inherit from base class
# ! only nice for our ABC but it looks ridiculous when inherit from
# ! grand-nth ancestors
autodoc_inherit_docstrings = False
add_module_names = False  # Remove namespaces from class/method signatures

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "TIA Toolbox"
copyright = "2021, TIA Lab"
author = "TIA Lab"

# The version info for the project you're documenting, acts as replacement
# for |version| and |release|, also used in various other places throughout
# the built documents.
#
# The short X.Y version.
version = tiatoolbox.__version__
# The full version, including alpha/beta/rc tags.
release = tiatoolbox.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output -------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

# Theme options are theme-specific and customize the look and feel of a
# theme further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    "sg_gallery.css",
]


def setup(app):
    # https: // github.com / sphinx - gallery / sphinx - gallery / pull / 845  # issuecomment-876102461
    # Force overwrite sg_gallery.css
    app.connect(
        "builder-inited", lambda app: app.config.html_static_path.append("_static")
    )
    app.add_stylesheet("sg_gallery.css")


# -- Options for HTMLHelp output ---------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "tiatoolboxdoc"


# -- Options for LaTeX output ------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto, manual, or own class]).
latex_documents = [
    (master_doc, "tiatoolbox.tex", "TIA Toolbox Documentation", "TIA Lab", "manual"),
]


# -- Options for manual page output ------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "tiatoolbox", "TIA Toolbox Documentation", [author], 1)]


# -- Options for Texinfo output ----------------------------------------

latex_engine = "xelatex"

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "tiatoolbox",
        "TIA Toolbox Documentation",
        author,
        "tiatoolbox",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# -- Options for InterSphinx (Reference Other Docs) --------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference/", None),
    "matplotlib": ("https://matplotlib.org", None),
    "sklearn": ("https://scikit-learn.org/stable/", None),
}

# create latex preample so that we can build arbitrary nested depth
fh = open("latex_preamble.tex", "r+")
PREAMBLE = fh.read()
fh.close()
latex_elements = {
    # Additional stuff for the LaTeX preamble.
    "preamble": PREAMBLE,
}

# -- Options for autodoc -----------------------------------------------

autodoc_typehints = "description"
autodoc_type_aliases = {
    "Iterable": "Iterable",
    "ArrayLike": "ArrayLike",
}


print("=" * 16)
print("Copy example notebooks into docs/_notebooks")
print("=" * 16)


def all_but_ipynb(dir_path, contents):
    """Helper to copy all .ipynb"""
    result = []
    for c in contents:
        flag = os.path.isfile(os.path.join(dir_path, c)) and (not c.endswith(".ipynb"))
        if flag:
            result += [c]
    return result


DOC_ROOT = os.path.dirname(os.path.realpath(__file__))
PROJ_ROOT = pathlib.Path(DOC_ROOT).parent
shutil.rmtree(os.path.join(PROJ_ROOT, "docs/_notebooks"), ignore_errors=True)
shutil.copytree(
    os.path.join(PROJ_ROOT, "examples"),
    os.path.join(PROJ_ROOT, "docs/_notebooks"),
    ignore=all_but_ipynb,
)
