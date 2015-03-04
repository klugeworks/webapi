import os
import unittest
import kluge_web
from flask_testing import TestCase
from flask import current_app

datastore_type = 'KlugeRedis'


class TestRoot(TestCase):
    test_app_name = 'ASR transcript demo'
    test_datastore_type = datastore_type

    def create_app(self):
        overrides = dict(
            SM_WEB_APP_NAME=self.test_app_name,
            SM_WEB_DATASTORE=self.test_datastore_type
        )
        app, api = kluge_web.create_app(
            cfg_module='kluge_web.default_settings.TestingConfig',
            cfg_overrides=overrides
        )
        return app

    def test_index(self):
        response = self.client.get('/')
        self.assert_status(response, 200)
        self.assertEquals(response.data, self.test_app_name)


class TestFileDown(TestCase):
    @staticmethod
    def create_app():
        app, api = kluge_web.create_app(
            cfg_module='kluge_web.default_settings.TestingConfig',
        )
        return app

    def test_get(self):
        response = self.client.get('/file')
        self.assertStatus(response, 200)
        sm_directory = os.path.dirname(os.path.realpath(kluge_web.__file__))
        sm_init_file = "%s/%s" % (sm_directory, "__init__.py")
        with open(sm_init_file, 'r') as open_sm_init_file:
            orig_source = open_sm_init_file.read()
            self.assertEquals(response.data, orig_source)


class TestFileUp(TestCase):
    @staticmethod
    def create_app():
        app, api = kluge_web.create_app(
            cfg_module='kluge_web.default_settings.TestingConfig',
        )
        return app

    def test_post(self):
        kl_directory = os.path.dirname(os.path.realpath(kluge_web.__file__))
        kl_init_file = "%s/%s" % (kl_directory, "__init__.py")
        with open(kl_init_file, 'r') as open_kl_init_file:
            open_kl_init_file.seek(0)
            response = self.client.post('/fileup', data=dict(bytes=open_kl_init_file, chunkid=1, language="english",
                                                             name="testname", queue="kluge_test_queue"))
            self.assertStatus(response, 200)
            self.assertEquals(response.data, '"testname"')


if __name__ == '__main__':
    unittest.main()