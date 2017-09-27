import unittest
from case_sims import Pedigree, year

famID_idx = 0
name_idx = 1
target_idx = 2
indivID_idx = 3
fathID_idx = 4
mothID_idx = 5
sex_idx = 6
twin_idx = 7
dead_idx = 8
age_idx = 9
birthYear_idx = 10
brCa_1_idx = 11
brCa_2_idx = 12
ovCa_idx = 13
proCa_idx = 14
panCa_idx = 15
gTest_idx = 16
mutn_idx = 17
ashkn_idx = 18
ER_idx = 19
PR_idx = 20
HER2_idx = 21
CK14_idx = 22
CK56_idx = 23

class test_pedigree_methods(unittest.TestCase):
    
    def setUp(self):

        self.gender = ["M", "F"]

        self.person = [1, 1, 0, 1, 0, 0, "M", 0, 0, 30, 1987, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.person2 = [1, 2, 0, 2, 0, 0, "F", 0, 0, 30, 1987, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
    def test_init_proband(self):
        '''
        Tests that: 
        1. Target is equal to 1
        2. Age is in age range specified in init_proband
        '''
        ped = Pedigree()
        proband = ped.init_proband()
        
        self.assertEqual(proband[target_idx], 1)

        self.assertIn(proband[age_idx], range(20, 66))
        
    def test_add_parents(self):
        '''
        Tests that:
        1. ValueError is raised when person already has parents
        2. Sex of each parent is correct
        3. FamID for person and parents is equal
        4. Target status is set to 0
        5. Dead status set correctly based on parent's age
        6. Birth year is set correctly based on age and dead status
        7. Age is in correct range based on child's age
        '''
        ped = Pedigree()
        self.person[fathID_idx] = 2 
        self.person[mothID_idx] = 3
        #ensures that a person is not assigned multiple sets of parents
        #fails if a person who already has parents is used as the arguement in add_parents
        with self.assertRaises(ValueError):
            parents = ped.add_parents(self.person)
            
        self.person[fathID_idx] = 0
        self.person[mothID_idx] = 0
        parents = ped.add_parents(self.person)

        #position of each parent in list parents
        fathPosition = 0
        mothPosition = 1
        
        self.assertEqual(parents[fathPosition][sex_idx], "M")
        self.assertEqual(parents[mothPosition][sex_idx], "F")

        for parent in parents:
            self.assertEqual(parent[famID_idx], self.person[famID_idx])
            
            self.assertEqual(parent[target_idx], 0)
            
            if parent[age_idx] > 90:
                self.assertEqual(parent[dead_idx], 1)
            else:
                self.assertEqual(parent[dead_idx], 0)
                self.assertEqual(parent[birthYear_idx], int(year) - int(parent[age_idx]))

            self.assertIn(parent[age_idx], range(self.person[age_idx] + 20, self.person[age_idx] + 41))

        self.person[fathID_idx] = 0
        self.person[mothID_idx] = 0
        #ensures that parent age must be greater than 90
        self.person[age_idx] = 71
        parents = ped.add_parents(self.person)

        #checking to make sure that if parent is dead, birth year is correct for actual year born
        for parent in parents:
            self.assertEqual(parent[dead_idx], 1)
            self.assertLessEqual(parent[birthYear_idx], int(year) - int(parent[age_idx]))
       
    def test_add_partner(self):
        '''
        Fix to match format in above tests

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
        Fix to match format above
        
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
        Fix to match new format
         
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

    def test_make_healthy_pedigree(self):
        '''
        Fix to match new test format
 
        Tests that:
        1. FamID same for every person in pedigree
        '''
        ped = Pedigree()

        pedigree = ped.make_healthy_pedigree()

        famID = pedigree[0][0]
       
        for person in pedigree:
            self.assertEqual(person[0], famID)
                        
            
