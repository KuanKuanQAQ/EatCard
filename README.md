# 规则
1. 桌上有 5 行牌，每个玩家 10 张牌。

2. 所有玩家同时各出 1 张牌，并按如下规则摆放到某一行末尾：

    2.1. 把所有玩家出的牌由小到大排序。

    2.2. 从中拿出最小的一张放在尾牌最接近且小于该牌的行的末尾。

    2.3. 如果没有满足此条件的行，则该玩家吃掉最小尾牌行所有牌。并将该牌作为该行新首牌。

    2.4. 如果经过 2.2. 的插入，该行长度大于 5，则该玩家吃掉前五张牌。

    2.5. 返回 2.1.

3. 一个玩家吃掉的牌按如下方法积分：
    
    3.1. 该牌被 11 整除记 5 分。

    3.2. 该牌被 10 整除记 3 分。
    
    3.3. 该牌不被 10 整除，却被 5 整除记 2 分。

    3.4. 其他牌记 1 分。

4. 玩家所有牌出完后，分数最高者输。

# 运行
* 需要 `curses` 库。

* 首先运行 `server.py`，根据提示输入玩家人数。

* 运行 `client.py` 启动客户端，启动数量与玩家人数相同。

# 界面
出牌输入：`-p xx`，xx 表示你要出的牌。
