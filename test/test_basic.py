import rdkit
import pubchempy as pcp

def test_imports():
    assert rdkit.__version__ is not None
    assert pcp.__name__ == 'pubchempy'

def test_rdkit_mol():
    from rdkit import Chem
    mol = Chem.MolFromSmiles('C[C@]12CCC(=O)C=C1CC[C@@H]3[C@@H]2[C@H](C[C@]4([C@H]3CC[C@@]4(C(=O)CO)O)C)O')
    assert mol is not None
    assert mol.GetNumAtoms() > 0
