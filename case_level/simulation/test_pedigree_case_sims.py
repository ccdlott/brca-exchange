import pytest
import unittest
from case_sims import Pedigree, year

class test_pedigree_methods(unittest.TestCase):

    def setUp(self):

        self.variable_defs = {
            "FamID" : 0,
            "Name" : 1,
            "Target" : 2,
            "IndivID" : 3,
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

        self.person2 = [1, 2, 0, 2, 0, 0, "F", 0, 0, 30, 1987, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
    def test_init_proband(self):
        '''
        Tests that: 
        1. Variables always set to zero in variable_zero list are equal to zero
        2. FamID, Name, and IndivID are greater or equal to 1
        3. Name and IndivID are equal
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
            elif name == "IndivID":
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
        2. Gender for each parent is correct
        3. FamID for person and parents is equal
        4. Name and IndivID are greater than zero and are equal
        5. Age in correct range based on child's age
        6. Birth year set correctly based on age
        7. Parent status changed to dead if dead
        8. All other variables set to zero
        '''
        ped = Pedigree()
        self.person[4] = 2 
        self.person[5] = 3
        with self.assertRaises(TypeError):
            parents = ped.add_parents(self.person)

        self.person[4] = 0
        self.person[5] = 0
        parents = ped.add_parents(self.person)

        self.assertEqual(parents[0][6], "M")
        self.assertEqual(parents[1][6], "F")
        
        for parent in parents:
            for name, index in self.variable_defs.iteritems():
                if name in self.variable_zero:
                    self.assertEqual(0, parent[index])
                elif name == "FamID":
                    self.assertEqual(self.person[0], parent[index])
                elif name == "Name":
                    self.assertGreaterEqual(parent[index], 1)
                elif name == "IndivID":
                    self.assertGreaterEqual(parent[index], 1)
                    self.assertEqual(parent[index], parent[index-2])
                elif name == "Sex":
                    self.assertIn(parent[index], self.gender)
                elif name =="Age":
                    person_age = self.person[index]
                    self.assertIn(parent[index], range(person_age + 20, person_age + 41))
                elif name == "Birth Year":
                    expected_birth_year = int(year) - int(parent[index-1])
                    self.assertEqual(expected_birth_year, parent[index])
                elif name == "Dead":
                    if parent[index+1] > 90:
                        self.assertEqual(1, parent[index])
                    else:
                        self.assertEqual(0, parent[index])
                else:
                    self.assertEqual(0, parent[index])

        
    def test_add_partner(self):
        '''
        Tests that:
        1. Gender of partner is correct
        2. FamID for person and partner is equal
        3. Name and IndivID are greater than zero and are equal
        4. Age in correct range based on person's age
        5. Birth year is set correctly based on age
        6. Dead status set to the correct value
        7. All other variables are equal to zero
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
            elif name == "IndivID":
                self.assertGreaterEqual(partner[index], 1)
                self.assertEqual(partner[index], partner[index-2])
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

    def test_add_offspring(self):
        '''
        Tests that:
        1. FathID and MothID for each child is set correctly based on gender
        2. FamID set correctly for each child
        3. Name and IndivID are equal and greater than 1
        4. Sex of child is set to either "M" or "F"
        5. Age is appropriate based on mother's age
        6. Child age is never less than 1
        7. Child birth year is set correctly
        8. Necessary variables in list are set to zero
        '''
        ped = Pedigree()

        self.person[6] = "M"
        self.person2[6] = "F"
        children = ped.add_offspring(self.person, self.person2)
        for child in children:
            self.assertEqual(child[4], self.person[3])
            self.assertEqual(child[5], self.person2[3])

        self.person[6] = "F"
        self.person2[6] = "M"
        children = ped.add_offspring(self.person, self.person2)
        for child in children:
            self.assertEqual(child[4], self.person2[3])
            self.assertEqual(child[5], self.person[3])

        for child in children:
            for name, index in self.variable_defs.iteritems():
                if name in self.variable_zero:
                    self.assertEqual(0, child[index])
                elif name == "FamID":
                    self.assertEqual(child[index], self.person[index])
                    self.assertEqual(child[index], self.person2[index])
                elif name == "Name":
                    self.assertGreaterEqual(child[index], 1)
                elif name == "IndivID":
                    self.assertGreaterEqual(child[index], 1)
                    self.assertEqual(child[index], child[index-2])
                elif name == "FathID":
                    self.assertEqual(child[index], self.person2[3])
                elif name == "MothID":
                    self.assertEqual(child[index], self.person[3])
                elif name == "Sex":
                    self.assertIn(child[index], self.gender)
                elif name == "Age":
                    self.assertIn(child[index], range(self.person[index]-40, self.person[index]-19))
                elif name == "Birth Year":
                    expected_birth_year = int(year)-int(child[index-1])
                    self.assertEqual(expected_birth_year, child[index])
                else:
                    self.assertEqual(0, child[index])
                    
    def test_add_siblings(self):
        '''
        Tests that:
        1. Person has parents or raises ValueError
        2. FamID is equal for person and siblings
        3. Name and IndivID are greater than zero and equal
        4. FathID and MothID are the same for person and siblings
        5. Age is in the correct range based on person's age
        6. Birth year is correctly set based on age
        7. Dead status is set to the correct value
        8. All other variables are equal to zero
        '''
        ped = Pedigree()

        self.person[4] = 0
        self.person[5] = 0
        with self.assertRaises(ValueError):
            siblings = ped.add_siblings(self.person)

        self.person[4] = 2
        self.person[5] = 3
        siblings = ped.add_siblings(self.person)

        for sibling in siblings:
            for name, index in self.variable_defs.iteritems():
                if name in self.variable_zero:
                    self.assertEqual(sibling[index], 0)
                elif name == "FamID":
                    self.assertEqual(sibling[index], self.person[index])
                elif name == "Name":
                    self.assertGreaterEqual(sibling[index], 1)
                elif name == "IndivID":
                    self.assertGreaterEqual(sibling[index], 1)
                    self.assertEqual(sibling[index], sibling[index-2])
                elif name == "FathID":
                    self.assertEqual(sibling[index], self.person[index])
                elif name == "MothID":
                    self.assertEqual(sibling[index], self.person[index])
                elif name == "Sex":
                    self.assertIn(sibling[index], self.gender)
                elif name == "Age":
                    self.assertIn(sibling[index], range(self.person[index]-15, self.person[index]+16))
                elif name == "Birth Year":
                    expected_birth_year = int(year) - int(sibling[index-1])
                    self.assertEqual(expected_birth_year, sibling[index])
                elif name == "Dead":
                    if sibling[index+1] > 90:
                        self.assertEqual(sibling[index], 1)
                    else:
                        self.assertEqual(sibling[index], 0)
                else:
                    self.assertEqual(sibling[index], 0)
