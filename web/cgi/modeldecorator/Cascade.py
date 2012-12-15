#coding=utf-8
from Decorator import Decorator
import site_helper as sh

# 级联操作，分别有increase(级联增加) decrease(级联减少) delete(级联删除)三种操作, 每种操作可以设置多对关联值, 每对关联值由一个表名和一个字段名组成
# 比如想让被装饰的model在insert时给t1表的a1字段加1,那么就设置increase=[('t1', 'a1'),]
# 如果想删除model时,也同时删除另一张表的关联数据,那么就使用delete(危险!)
# data需有一个other_table的主键值用于与另一个表的数据关联

class Cascade(Decorator):
    ''' decorator = [
        ('Cascade',dict(
            delete  =[('other_table', 'attr'), ],
            increase=[('other_table', 'attr'), ],
            decrease=[('other_table', 'attr'), ]
        ),
    ] '''

    def insert(self, data):
        new_id = self.model.insert(data)
        if self.arguments.has_key('increase'):
            assert(all(lambda x:len(x)==2, self.arguments.increase))
            for other_table, attr in self.arguments.increase:
                self.__otherInc(data, other_table, attr, 1)
        return new_id

    def delete(self, item_id):
        if self.arguments.has_key('decrease'):
            assert(all(lambda x:len(x)==2, self.arguments.decrease))
            for other_table, attr in self.arguments.decrease:
                self.__otherInc(data, other_table, attr, -1)

        ret = self.model.delete(item_id)

        if self.arguments.has_key('delete'):
            assert(all(lambda x:len(x)==2, self.arguments.delete))
            for other_table, attr in self.arguments.decrease:
                other_model = sh.model(other_table)
                query = other_model.replaceAttr('delete from {$table_name} where %sid=%%s' % self.getModelTableName())
                other_model.delete(query, [item_id])

        return ret

    def __otherInc(self, data, other_table, attr, increment):
        other_id = data.get(other_table+'id', None)
        if other_id:
            other_model = sh.model(other_table)
            other_item = other_model.get(other_id)
            if other_item:
                other_model.update(other_id, {attr: other_item[attr] + increment})
                return True
        return False