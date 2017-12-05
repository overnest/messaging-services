import unittest
import transaction

from pyramid import testing

from .tus import parse_metadata, InvalidUploadMetadata


def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('.models')
        settings = self.config.get_settings()

        from .models import (
            get_engine,
            get_session_factory,
            get_tm_session,
        )

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)

        self.session = get_tm_session(session_factory, transaction.manager)

    def init_database(self):
        from .models.meta import Base
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        from .models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)


class TusTest(unittest.TestCase):
    def test_metadata_parsed_successfully(self):
        headers = {'Upload-Metadata': "to bmluamE="}
        result = parse_metadata(headers)
        self.assertTrue(len(result) == 1)
        self.assertEqual(result['to'], "ninja")

    def test_multiple_valid_keys_parsed(self):
        headers = {'Upload-Metadata': "to bmluamE=,foo YmFy"}
        result = parse_metadata(headers)
        self.assertTrue(len(result) == 2)
        self.assertEqual(result['to'], "ninja")
        self.assertEqual(result['foo'], "bar")

    def test_empty_metadata_is_fine(self):
        headers = {'Upload-Metadata': ""}
        result = parse_metadata(headers)
        self.assertTrue(len(result) == 0)

    def test_wrong_length_of_pair_raises_error(self):
        headers = {'Upload-Metadata': "to bmluamE= blah"}

        with self.assertRaisesRegex(InvalidUploadMetadata, "key-value pairs"):
            parse_metadata(headers)

    def test_duplicate_keys_raises_error(self):
        headers = {'Upload-Metadata': "to bmluamE=,to ymxhaA==,foo YmFy"}

        with self.assertRaisesRegex(InvalidUploadMetadata, "unique"):
            parse_metadata(headers)

    def test_base64_issues_raise_error(self):
        headers = {'Upload-Metadata': "to ninja"}

        with self.assertRaisesRegex(InvalidUploadMetadata, "Base64"):
            parse_metadata(headers)
