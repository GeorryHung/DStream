import sys
sys.path.append("..")

from Helper import *
import unittest
from TestHelper import  *
from Grid import *
# =========================================Test Code============================================

class TestGrid(unittest.TestCase):
    def test_key(self):
        # TODO:制造100个随机的合法rawData，测key（）函数能否正确返回该key值
        for i in range(1, 100 + 1):
            rawData = HelperForTest.randomLegalRawData()
            right_key = Helper().getKeyFromRawData(rawData)
            g = Grid()
            g.addData(rawData, random.randint(1,10000))
            totest_key =g.key()
            self.assertEqual(right_key,totest_key)
    def test_cluster(self):
        #TODO：给他随便设置一个cluster，测试cluster的get和isNoCluster
        g=Grid()
        rawData = HelperForTest.randomLegalRawData()
        right_key = Helper().getKeyFromRawData(rawData)
        self.assertTrue(g.isNoCluster())
        g.setClusterKey(right_key)
        self.assertEqual(g.clusterKey(),right_key)

    def test_time_remove(self):
        g=Grid()
        t=random.randint(1,10000)
        g.setRemoveTime(t)
        self.assertEqual(t,g.time_remove())



    def test_SparseStatus(self):
        g=Grid()
        g.setSparseStatus(SparseStatus.TODELETE)
        self.assertEqual(g.sparseStatus(),SparseStatus.TODELETE)
        g.setSparseStatus(SparseStatus.TEMP)
        self.assertEqual(g.sparseStatus(),SparseStatus.TEMP)
        g.setSparseStatus(SparseStatus.NORMAL)
        self.assertEqual(g.sparseStatus(),SparseStatus.NORMAL)

    def test_addData_time(self):
        #检查addData后若time小于之前的更新时间，是否会抛出异常
        g=Grid()
        g._Grid__time_update=1000
        with self.assertRaisesRegex(ValueError,"time_update"):
            raw=HelperForTest.randomLegalRawData()
            g.addData(raw,500)


    #检查grid经过addData后，key值是否正确
    def test_addData_key(self):

        #TODO：add之后检查key是否正确，检查错误的rawData抛出异常，检查当前更新时间是否正确、想办法测试change，测试TODELETE
        g=Grid()
        rawData=HelperForTest.randomLegalRawData()
        correct_key=Helper.getKeyFromRawData(rawData)
        g.addData(rawData,1)
        self.assertEqual(correct_key,g.key())
        self.assertEqual(1,g._Grid__time_update)

    def test_addData_wrongKey(self):
        g=Grid()
        rawData=HelperForTest.randomLegalRawData()
        g.addData(rawData,1)
        #换一个key，测错误的key抛出异常
        anotherRawData=HelperForTest.anotherKeyRawdataFromKey(rawData)
        with self.assertRaises(ValueError):
            g.addData(anotherRawData,2)

    # 检查当前更新时间是否正确
    def test_addData_timeUpdate(self):
        g = Grid()
        t=1
        rawData=HelperForTest.randomLegalRawData()
        for i in range(1,50):
            t+=random.randint(1,500)
            g.addData(rawData,t)
            self.assertEqual(g._Grid__time_update,t)




    #检查densityStatus的get方法是否正确
    def test_densityStatus(self):
        g = Grid()
        g._Grid__densityStatus=DensityStatus.SPARSE
        self.assertEqual(DensityStatus.SPARSE,g.densityStatus())

        g._Grid__densityStatus=DensityStatus.DENSE
        self.assertEqual(DensityStatus.DENSE,g.densityStatus())

        g._Grid__densityStatus=DensityStatus.TRANSITIONAL
        self.assertEqual(DensityStatus.TRANSITIONAL,g.densityStatus())

    # 检查addData的逻辑里各个参数的变更
    def test_addData_changeAndDensity(self):
        #测试Dense
        rawData=HelperForTest.randomLegalRawData()
        g=Grid()
        g._Grid__change=0
        g._Grid__densityStatus=DensityStatus.SPARSE
        g._Grid__density=Helper().Dm+100
        g._Grid__time_update=1 #上次更新时间和当前时间相同，保证density不会太多的改变，更利于测试
        self.assertEqual(g.density(),Helper().Dm+100)
        g.addData(rawData,2)
        self.assertEqual(g._Grid__change,1)
        self.assertEqual(DensityStatus.DENSE,g.densityStatus())

        #测试Sparse
        g._Grid__change=0
        g._Grid__densityStatus = DensityStatus.DENSE
        g._Grid__density=Helper.Dl-100
        g.addData(rawData, 3)
        self.assertEqual(g._Grid__change,1)
        self.assertEqual(DensityStatus.SPARSE, g.densityStatus())


        #测试Transitinal
        g._Grid__change = 0
        g._Grid__densityStatus = DensityStatus.DENSE
        g._Grid__density = Helper().Dl+(Helper().Dl+Helper().Dm)/2
        self.assertGreater(g.density(),Helper().Dl)
        self.assertLess(g.density(),Helper().Dm)


        g.addData(rawData,4)

        self.assertEqual(g._Grid__change,1)
        self.assertEqual(DensityStatus.TRANSITIONAL,g.densityStatus())

        g._Grid__change = 0
        g._Grid__densityStatus = DensityStatus.SPARSE
        g._Grid__density = Helper.Dl + (Helper.Dl + Helper.Dm) / 2
        g.addData(rawData, 5)
        self.assertEqual(g._Grid__change, 1)
        self.assertEqual(DensityStatus.TRANSITIONAL, g.densityStatus())

        #测试TODELETE
        g._Grid__sparseStatus=SparseStatus.TODELETE
        g.addData(rawData,6)
        self.assertEqual(g._Grid__sparseStatus,SparseStatus.TEMP)

        g._Grid__sparseStatus = SparseStatus.NORMAL
        g.addData(rawData, 7)
        self.assertEqual(g._Grid__sparseStatus, SparseStatus.NORMAL)

        g._Grid__sparseStatus = SparseStatus.TEMP
        g.addData(rawData, 8)
        self.assertEqual(g._Grid__sparseStatus, SparseStatus.TEMP)


    def test_clear(self):
        g=Grid()
        g._Grid__cluster_key = 10000000000
        g._Grid__density = 10000000000
        g._Grid__change =10000000000
        g._Grid__densityStatus = DensityStatus.DENSE
        g._Grid__sparseStatus = SparseStatus.TODELETE
        g._Grid__time_remove = 1000000000
        g._Grid__time_update = 1000000000
        g.clear()

        self.assertEqual(g._Grid__cluster_key,-1)
        self.assertEqual(g._Grid__key,0)
        self.assertEqual(g._Grid__change, 0)
        self.assertEqual(g._Grid__time_remove,0)
        self.assertEqual(g._Grid__time_update,0)
        self.assertEqual(g._Grid__densityStatus,DensityStatus.SPARSE)
        self.assertEqual(g._Grid__sparseStatus,SparseStatus.NORMAL)

    def test_densityThreshold(self):
        last_time = random.randint(1, 10000)
        cur_time=last_time+random.randint(1,10000)

        value=Helper().Cl*(1-Helper().lamb**(cur_time-last_time+1))/(Helper().N*(1-Helper().lamb))
        g=Grid()
        g._Grid__time_update=last_time

        self.assertEqual(value,g.densityThreshold(cur_time))

    def test_resetChangeFlag(self):
        g=Grid()
        g._Grid__change=1
        g.resetChangeFlag()
        self.assertEqual(0,g._Grid__change)


    def test_density(self):
        g=Grid()
        a=random.randint(1, 500)
        g._Grid__density=a
        self.assertEqual(a,g.density())
        self.assertGreater(g.density(),0)


    def test_densityWithTime(self):
        g=Grid()
        g._Grid__time_update=2
        value=g._Grid__density*(Helper().lamb**(5-2))
        self.assertEqual(value,g.densityWithTime(5))
    def test_change(self):
        g=Grid()
        g._Grid__change=random.randint(1,1000)
        self.assertEqual(g._Grid__change,g.change())

if __name__ =="__main__":
    unittest.main()





