# How to make a release

`jupyterhub-kerberosauthenticator` is a package available on [PyPI][].
These are instructions on how to make a release.

## Pre-requisites

- Push rights to [jupyterhub/kerberosauthenticator][]

## Steps to make a release

1. Create a PR updating `CHANGELOG.md` with [github-activity][] and
   continue only when its merged.

   ```shell
   github-activity jupyterhub/kerberosauthenticator
   ```

1. Checkout main and make sure it is up to date.

   ```shell
   git checkout main
   git fetch origin main
   git reset --hard origin/main
   ```

1. Create and push a git tag. setuptools-scm automatically sets the Python package version from the tag.

   ```shell
   git tag -s ${VERSION} -m ${VERSION}
   git push origin ${VERSION}
   ```

   Following this, the [CI system][] will build and publish a release.

[pypi]: https://pypi.org/project/jupyterhub-kerberosauthenticator/
[jupyterhub/kerberosauthenticator]: https://github.com/jupyterhub/kerberosauthenticator
[github-activity]: https://github.com/executablebooks/github-activity
[ci system]: https://github.com/jupyterhub/kerberosauthenticator/actions/workflows/build.yaml
