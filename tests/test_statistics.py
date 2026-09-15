"""Small statistical safeguards: missing denominators, boundary rates, known Fisher example."""
import sys
from pathlib import Path
import unittest
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyze import binary_comparison,holm,wilson


class StatisticsTests(unittest.TestCase):
    def test_unknown_is_not_failure(self):
        frame=pd.DataFrame({'group':['human','human','ai','ai'],'dated_promise':[1,None,0,1]})
        result=binary_comparison(frame,'dated_promise')
        self.assertEqual(result['human']['n'],1)
        self.assertEqual(result['human']['unknown_or_na'],1)
        self.assertEqual(result['comparison']['difference_pp'],-50)

    def test_no_observations_has_no_comparison(self):
        result=binary_comparison(pd.DataFrame({'group':['human','ai'],'dated_promise':[None,0]}),'dated_promise')
        self.assertIsNone(result['human']['rate'])
        self.assertNotIn('comparison',result)

    def test_zero_events_does_not_mean_zero_uncertainty(self):
        low,high=wilson(0,50)
        self.assertAlmostEqual(low,0)
        self.assertGreater(high,.07)
        self.assertLess(high,.08)

    def test_documented_fisher_example(self):
        # SciPy documentation example: [[6,2],[1,4]].
        frame=pd.DataFrame({'group':['ai']*8+['human']*5,'dated_promise':[1]*6+[0]*2+[1]+[0]*4})
        result=binary_comparison(frame,'dated_promise')
        self.assertAlmostEqual(result['comparison']['fisher_two_sided_p'],0.10256410256410256)

    def test_holm_is_monotone_and_capped(self):
        # Sorted a<c<b<d: 4*.01, 3*.03, max(.09, 2*.04), max(.09, 1*.9).
        adjusted=holm({'a':.01,'b':.04,'c':.03,'d':.9})
        self.assertAlmostEqual(adjusted['a'],.04)
        self.assertAlmostEqual(adjusted['c'],.09)
        self.assertAlmostEqual(adjusted['b'],.09)
        self.assertEqual(adjusted['d'],.9)


if __name__=='__main__':
    unittest.main()
