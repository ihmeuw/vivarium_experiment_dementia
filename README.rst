===============================
vivarium_experiment_dementia
===============================

Research repository for the vivarium_experiment_dementia project.

.. contents::
   :depth: 1

Model Documentation Resources
-----------------------------

**You should put links to the concept model documentation and any other**
**relevant documentation here.**

Installation
------------

These models require data from GBD databases. You'll need several internal
IHME packages and access to the IHME cluster.

To install the extra dependencies create a file called ~/.pip/pip.conf which
looks like this::

    [global]
    extra-index-url = http://pypi.services.ihme.washington.edu/simple
    trusted-host = pypi.services.ihme.washington.edu


To set up a new research environment, open up a terminal on the cluster and
run::

    $> conda create --name=vivarium_experiment_dementia python=3.6
    ...standard conda install stuff...
    $> conda activate vivarium_experiment_dementia
    (vivarium_experiment_dementia) $> conda install redis
    (vivarium_experiment_dementia) $> git clone git@github.com:ihmeuw/vivarium_experiment_dementia.git
    ...you may need to do username/password stuff here...
    (vivarium_experiment_dementia) $> cd vivarium_experiment_dementia
    (vivarium_experiment_dementia) $> pip install -e .


Usage
-----

You'll find four directories inside the main
``src/vivarium_experiment_dementia`` package directory:

- ``components``

  This directory is for Python modules containing custom components for
  the vivarium_experiment_dementia project. You should work with the
  engineering staff to help scope out what you need and get them built.

- ``external_data``

  If you have **small scale** external data for use in your sim or in your
  results processing, it can live here. This is almost certainly not the right
  place for data, so make sure there's not a better place to put it first.

- ``model_specifications``

  This directory should hold all model specifications and branch files
  associated with the project.

- ``verification_and_validation``

  Any post-processing and analysis code or notebooks you write should be
  stored in this directory.

