class puyo_simulator():
    _X_LIMIT_MIN = 0
    _X_LIMIT_MAX = 6
    _Y_LIMIT_MIN = 0
    _Y_LIMIT_MAX = 12
    OJAMA = 6
    field = [[0]*6 for _ in range(12)]
    num_puyo = 0
    num_puyo_after_chain = 0
    
    def count_puyo(self):
        num_puyo = 0
        for y in self.field:
            for x in y:
                if x > 0:
                    num_puyo += 1
        return num_puyo
    
    def search(self, x, y, color, searched_list):
        """引数x,yの座標にあるぷよと同じ色を探索し、連結しているぷよをリストにして返す.
        Args:
            x (int): fieldのx座標
            y (int): fieldのy座標
            color (int): 色情報
            searched_list (list): 探索済み場所の、ぷよの座標
        Return:
            searched_list(list)
        """
        if self.field[y][x] == 0 or self.field[y][x] == self.OJAMA:
            return
        if self.field[y][x] != color:
            return
        if (x,y) in searched_list:
            return
        searched_list.append((x,y))
        if x > self._X_LIMIT_MIN:
            self.search(x-1,y,color,searched_list)
        if x < self._X_LIMIT_MAX-1:
            self.search(x+1,y,color,searched_list)
        if y > self._Y_LIMIT_MIN:
            self.search(x,y-1,color,searched_list)
        if y < self._Y_LIMIT_MAX-1:
            self.search(x,y+1,color,searched_list)
        return searched_list
    
    def _ojama_erase(self, x, y):
        dxdy = [[0,1],[1,0],[0,-1],[-1,0]] # 4方向
        for dx,dy in dxdy:
            if x+dx < self._X_LIMIT_MIN or x+dx >= self._X_LIMIT_MAX:
                continue
            if y+dy < self._Y_LIMIT_MIN or y+dy >= self._Y_LIMIT_MAX:
                continue
            if self.field[y+dy][x+dx] == self.OJAMA:
                self.field[y+dy][x+dx] = 0

    def erase(self, n=4):
        """nこ以上つながっているぷよを消し、消す個数を返す。
        Args: 
            n(int): n以上なら消えるとする. 
        Return:
            num_erase(int): 消える個数 
        """
        num_erase = 0
        for y in range(self._Y_LIMIT_MAX):
            for x in range(self._X_LIMIT_MAX):
                searched_list = []
                # 座標x,yを起点にして、同色のぷよを探索
                searched_list = self.search(x,y,self.field[y][x],searched_list)
                if searched_list != None and len(searched_list) >= n:
                    for xy in searched_list:
                        num_erase += 1
                        self.field[xy[1]][xy[0]] = 0
                        self._ojama_erase(xy[0], xy[1])
        return num_erase
    
    def fall(self):
        """浮いているぷよを落下させる.
        Return:
            (bool): ぷよが落下したかどうか(落下=True)
        """
        for i in range(self._X_LIMIT_MAX):
            is_fall = False
            over_null = 0
            for j in range(self._Y_LIMIT_MAX-1, -1, -1):
                if self.field[j][i] == 0:
                    if is_fall == False:
                        over_null = j
                        is_fall = True
                else:
                    if is_fall:
                        self.field[over_null][i] = self.field[j][i]
                        self.field[j][i] = 0
                        over_null -= 1

    def chain(self):
        """連鎖を発火し、連鎖数をカウント.
        Returns:
            num_chain(int) : 連鎖数の結果
        """
        num_chain = 0
        while True:
            erase_num = self.erase()
            self.fall()
            if erase_num > 0:
                num_chain += 1
            else:
                break
        return num_chain
