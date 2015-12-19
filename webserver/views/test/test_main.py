from __future__ import absolute_import
from webserver.testing import ServerTestCase
from flask import url_for


class MainViewsTestCase(ServerTestCase):

    def test_index(self):
        resp = self.client.get(url_for('main.index'))
        self.assert200(resp)
