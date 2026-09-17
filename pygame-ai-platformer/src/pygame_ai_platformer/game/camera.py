"""横スクロール用のカメラ。

プレイヤーが画面中央より右へ進んだらカメラが追従する、
marioproto.py のスクロール処理をそのままクラス化したもの。
"""


class Camera:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.x = 0

    def reset(self):
        self.x = 0

    def update(self, player_rect):
        if player_rect.centerx - self.x > self.screen_width // 2:
            self.x = player_rect.centerx - self.screen_width // 2

    def apply(self, rect):
        """ワールド座標のrectをスクリーン座標に変換して返す(描画用)"""
        return rect.move(-self.x, 0)
