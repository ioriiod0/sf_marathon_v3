### START:
用于通知ai比赛开始

- API
```
POST /start
```

- Header
```
Content-Type: application/json	
```

- Body
```json
{}
```

- Response
```json
{}
```

### STEP:
比赛正式开始后每个回合调用，输入为当前游戏状态，输出为AI决策的动作

- API
```
POST /step
```

- Header
```
Content-Type: application/json	
```

- Body
```json
{
    'player1': { //玩家信息
        'name': 'p1', //玩家名
        'x': 8, //小哥所在位置X坐标
        'y': 4, //小哥所在位置Y坐标
        'home_x': 5, //小哥大本营所在位置X坐标
        'home_y': 5, //小哥大本营所在位置Y坐标
        'n_jobs': 10, //小哥背包包裹数
        'value': 99.0, //小哥背包包裹总价值
        'score': 0 //小哥得分
    },
    'player2': ..., // 同player1
    'walls': [   //障碍物所在位置
        {'x': 0, 'y': 1}, //障碍物X,Y坐标
        {'x': 0, 'y': 6}, 
        ...],
    
    'jobs': [
        {'x': 0, 'y': 2, 'value': 7.0}, //包裹所在位置，及其价值
        {'x': 0, 'y': 8, 'value': 9.0},
        ...
    ]
}
```

- Response
```json
{
    'action':'U' //取值范围为U,D,L,R,S 分别对应上，下，左，右，停留
}
```



### END:
用于通知ai比赛开始

- API
```
POST /end
```

- Header
```
Content-Type: application/json	
```

- Body
```json
{
    'player1': { //玩家信息
        'name': 'p1', //玩家名
        'x': 8, //小哥所在位置X坐标
        'y': 4, //小哥所在位置Y坐标
        'home_x': 5, //小哥大本营所在位置X坐标
        'home_y': 5, //小哥大本营所在位置Y坐标
        'n_jobs': 10, //小哥背包包裹数
        'value': 99.0, //小哥背包包裹总价值
        'score': 0 //小哥得分
    },
    'player2': ..., // 同player1
    'walls': [   //障碍物所在位置
        {'x': 0, 'y': 1}, //障碍物X,Y坐标
        {'x': 0, 'y': 6}, 
        ...],
    
    'jobs': [
        {'x': 0, 'y': 2, 'value': 7.0}, //包裹所在位置，及其价值
        {'x': 0, 'y': 8, 'value': 9.0},
        ...
    ]
}
```

- Response
```json
{}
```