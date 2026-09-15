"""Check published data contracts, rather than reproducing labeling logic."""
import unittest
from pathlib import Path
import pandas as pd

PATH = Path(__file__).resolve().parents[1] / 'data/analytic.csv'


@unittest.skipUnless(PATH.exists(), 'Final table not yet constructed')
class DatasetContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = pd.read_csv(PATH)

    def test_supplied_sample_complete(self):
        self.assertEqual(self.data.groupby('group').size().to_dict(), {'ai': 50, 'human': 50})
        self.assertTrue(self.data.call_id.is_unique)
        self.assertTrue(self.data.duration_seconds.gt(0).all())

    def test_critical_label_constraints(self):
        promised = self.data.dated_promise.eq(1)
        self.assertTrue(self.data.loc[promised, 'explicit_promise'].eq(1).all())
        self.assertTrue(self.data.loc[self.data.objection.ne(1), 'relevant_response'].isna().all())
        self.assertTrue(self.data.review_status.eq('transcript_reviewed').all())

    def test_no_private_text_fields(self):
        forbidden = {'source', 'sha256', 'text', 'evidence', 'segments', 'email', 'phone', 'name'}
        self.assertFalse(forbidden & set(self.data.columns))
        self.assertTrue(self.data.call_id.str.fullmatch(r'(human|ai)_\d{3}').all())


if __name__ == '__main__':
    unittest.main()
