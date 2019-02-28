from haystack import indexes
from df_goods.models import GoodsInfo
'''
class BookInfoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    def get_model(self):
        return BookInfo

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
'''
# 指定对于某个类的某些数据建立索引
class GoodsInfoIndex(indexes.SearchIndex, indexes.Indexable):
    # document=True指定此属性为索引字段，use_template=True说明生成索引的依据放在一个文件中
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        # 返回模型类类名
        return GoodsInfo

    # 指定这个函数返回的内容生成索引文件
    def index_queryset(self, using=None):
        return self.get_model().objects.all()