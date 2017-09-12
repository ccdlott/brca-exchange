import pytest
import unittest
import pdb
from case_sims import Pedigree, year

class test_pedigree_methods(unittest.TestCase):

    def setUp(self):

        self.variable_defs = {
            "FamID" : 0,
            "Name" : 1,
            "Target" : 2,
            "IndID" : 3,
            "FathID" : 4,
            "MothID" : 5,
            "Sex" : 6,
            "Twin" : 7,
            "Dead" : 8,
            "Age" : 9,
            "Birth Year" : 10,
            "BrCa_1" : 11,
            "BrCa_2" : 12,
            "OvCa" : 13,
            "ProCa" : 14,
            "PanCa" : 15,
            "G Test" : 16,
            "Mutn" : 17,
            "Ashkn" : 18,
            "ER" : 19,
            "PR" : 20,
            "HER2" : 21,
            "CK14" : 22,
            "CK56" : 23
            }
        
        self.variable_zero = ["Twin", "PanCa", "ProCa", "Ashkn", "ER", "PR", "HER2", "CK14", "Ck56"]

        self.gender = ["M", "F"]
        
        self.pro_age_range = range(20,66)

        self.person = [1, 1, 0, 1, 0, 0, "M", 0, 0, 30, 1987, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


        
    def test_init_proband(self):
        '''
        Tests that: 
        1. Variables always set to zero in variable_zero list are equal to zero
        2. FamID, Name, and IndID are greater or equal to 1
        3. Name and IndID are equal
        4. Target is set to 1
        5. Sex is set to either "M" or "F"
        6. Age is in age range specified in init_proband
        7. Birth year is set correctly based on age
        8. All other variables are equal to zero
        9. Tests age edge cases
        '''
        ped = Pedigree()
        proband = ped.init_proband()
        for name, index in self.variable_defs.iteritems():
            if name in self.variable_zero:
                self.assertEqual(0, proband[index])
            elif name == "FamID":
                self.assertGreaterEqual(proband[index], 1)
            elif name == "Name":
                self.assertGreaterEqual(proband[index], 1)
            elif name == "IndID":
                self.assertGreaterEqual(proband[index], 1)
                self.assertEqual(proband[index], proband[index-2])
            elif name == "Target":
                self.assertEqual(1, proband[index])
            elif name == "Sex":
                self.assertIn(proband[index], self.gender)
            elif name =="Age":
                self.assertIn(proband[index], self.pro_age_range)
            elif name == "Birth Year":
                expected_birth_year = int(year) - int(proband[9])
                self.assertEqual(expected_birth_year, proband[index])
            else:
                self.assertEqual(0, proband[index])

        proband[9] = 65
        self.assertIn(proband[9], self.pro_age_range)
        proband[9] = 20
        self.assertIn(proband[9], self.pro_age_range)
        proband[9] = 66
        self.assertNotIn(proband[9], self.pro_age_range)
        proband[9] = 19
        self.assertNotIn(proband[9], self.pro_age_range)

    def test_add_parents(self):
        '''
        Tests that:
        1. TypeError is raised when person already has parents
        2. FamID for person and parents is equal
        3. Name and IndID are greater than zero and are equal
        4. Target is equal to zero
        5. Gender for each parent is correct
        6. Age in correct range based on child's age
        7. Birth year set correctly based on age
        8. Parent status changed to dead if dead
        9. All other variables set to zero
        '''
        ped = Pedigree()
        self.person[4] = 2 
        self.person[5] = 3
        with self.assertRaises(TypeError):
            parents = ped.add_parents(self.person)

        self.person[4] = 0
        self.person[5] = 0
        parents = ped.add_parents(self.person)

        for name, index in self.variable_defs.iteritems():
            if name in self.variable_zero:
                self.assertEqual(0, parents[0][index])
                self.assertEqual(0, parents[1][index])
            elif name == "FamID":
                self.assertEqual(self.person[0], parents[0][index])
                self.assertEqual(self.person[0], parents[1][index])
            elif name == "Name":
                self.assertGreaterEqual(parents[0][index], 1)
                self.assertGreaterEqual(parents[1][index], 1)
            elif name == "IndID":
                self.assertGreaterEqual(parents[0][index], 1)
                self.assertGreaterEqual(parents[1][index], 1)
                self.assertEqual(parents[0][index], parents[0][index-2])
                self.assertEqual(parents[1][index], parents[1][index-2])
            elif name == "Target":
                self.assertEqual(0, parents[0][index])
                self.assertEqual(0, parents[1][index])
            elif name == "Sex":
                self.assertEqual(parents[0][index], "M")
                self.assertEqual(parents[1][index], "F")
            elif name =="Age":
                person_age = self.person[index]
                self.assertIn(parents[0][index], range(person_age + 20, person_age + 41))
                self.assertIn(parents[1][index], range(person_age + 20, person_age + 41))
            elif name == "Birth Year":
                fath_expected_birth_year = int(year) - int(parents[0][index-1])
                self.assertEqual(fath_expected_birth_year, parents[0][index])
                moth_expected_birth_year = int(year) - int(parents[1][index-1])
                self.assertEqual(moth_expected_birth_year, parents[1][index])
            elif name == "Dead":
                if parents[0][index+1] > 90:
                    self.assertEqual(1, parents[0][index])
                else:
                    self.assertEqual(0, parents[0][index])
                if parents[1][index+1] > 90:
                    self.assertEqual(1, parents[1][index])
                else:
                    self.assertEqual(0, parents[1][index])
            else:
                self.assertEqual(0, parents[0][index])
                self.assertEqual(0, parents[1][index])

        
    def test_add_partner(self):
        '''
        Tests that:
        1. Gender of partner is correct
        2. FamID for person and partner is equal
        3. Name and IndID are greater than zero and are equal
        4. Target is equal to zero
        5. Age in correct range based on person's age
        6. Birth year is set correctly based on age
        7. Dead status set to the correct value
        8. All other variables are equal to zero
        '''
        ped = Pedigree()
        
        self.person[6] = "M"
        partner = ped.add_partner(self.person)
        self.assertEqual(partner[6], "F")

        self.person[6] = "F"
        partner = ped.add_partner(self.person)
        self.assertEqual(partner[6], "M")
        
        for name, index in self.variable_defs.iteritems():
            if name in self.variable_zero:
                self.assertEqual(0, partner[index])
            elif name == "FamID":
                self.assertGreaterEqual(partner[index], self.person[index])
            elif name == "Name":
                self.assertGreaterEqual(partner[index], 1)
            elif name == "IndID":
                self.assertGreaterEqual(partner[index], 1)
                self.assertEqual(partner[index], partner[index-2])
            elif name == "Target":
                self.assertEqual(0, partner[index])
            elif name == "Sex":
                self.assertIn(partner[index], self.gender)
            elif name =="Age":
                self.assertIn(partner[index], range(self.person[index]-15, self.person[index]+16))
            elif name == "Birth Year":
                expected_birth_year = int(year) - int(partner[index-1])
                self.assertEqual(expected_birth_year, partner[index])
            elif name == "Dead":
                if partner[index+1] > 90:
                    self.assertEqual(partner[index], 1)
                else:
                    self.assertEqual(partner[index], 0)
            else:
                self.assertEqual(0, partner[index])
