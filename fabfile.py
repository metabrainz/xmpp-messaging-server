from __future__ import with_statement
from fabric.api import local
from fabric.colors import green, yellow


def git_pull():
    local("git pull origin")
    print(green("Updated local code.", bold=True))


def install_requirements():
    local("pip install -r requirements.txt")
    print(green("Installed requirements.", bold=True))


def build_static():
    local("./node_modules/.bin/gulp")
    print(green("Static files have been built successfully.", bold=True))


def deploy():
    git_pull()
    install_requirements()
    build_static()


def test(coverage=True):
    """Run all tests.

    It will also create code coverage report, unless specified otherwise. It
    will be located in cover/index.html file.
    """
    if coverage:
        local("nosetests --exe --with-coverage --cover-erase --cover-html "
              "--cover-package=webserver")
        print(yellow("Coverage report can be found in cover/index.html file.", bold=True))
    else:
        local("nosetests --exe")
