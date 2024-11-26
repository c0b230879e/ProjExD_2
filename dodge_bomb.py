import os
import random
import sys
import pygame as pg
import time

WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で与えられたRectが画面の中か外かを判定する
    引数：こうかとんRect or 爆弾Rect
    戻り値：真理値タプル（横，縦）／画面内：True，画面外：False
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate


"""
gameover画面を表示する関数
引数  screen
戻り値  なし
"""
def game_over(screen: pg.Surface) -> tuple[int, int]:  # Corrected syntax
    bl_img = pg.Surface((WIDTH, HEIGHT)) 
    pg.draw.rect(bl_img, (0, 0, 0), pg.Rect(0, 0, WIDTH, HEIGHT))
    bl_img.set_alpha(128)
    go_font = pg.font.Font(None, 80)
    txt = go_font.render("Game_Over", True, (255, 255, 255))
    cry_img = pg.image.load("fig/8.png")
    cry_rct = cry_img.get_rect()
    cry_rct2 = cry_img.get_rect()
    cry_rct.topleft = (WIDTH - 360) / 2, HEIGHT / 2
    cry_rct2.topleft = (WIDTH + 380) / 2, HEIGHT / 2
    bl_rct = bl_img.get_rect()
    bl_rct.topleft = 0, 0
    screen.blit(bl_img, bl_rct)
    screen.blit(txt, [(WIDTH - 270) / 2, HEIGHT / 2])
    screen.blit(cry_img, cry_rct)
    screen.blit(cry_img, cry_rct2)

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20))  # 爆弾用の空Surface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 爆弾円を描く
    bb_img.set_colorkey((0, 0, 0))  # 四隅の黒を透過させる
    bb_rct = bb_img.get_rect()  # 爆弾Rectの抽出
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5  # 爆弾速度ベクトル
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
            

       
        if kk_rct.colliderect(bb_rct):  # こうかとんと爆弾が重なっていたら
            print("ゲームオーバー")
            game_over(screen)  # ゲームオーバー画面表示
            pg.display.update()
            time.sleep(5)
            return  # ゲームオーバー
        
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key] == True:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]
        kk_rct.move_ip(sum_mv)
        # こうかとんが画面外なら，元の場所に戻す
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)
        bb_rct.move_ip(vx, vy)  # 爆弾動く
        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横にはみ出てる
            vx *= -1
        if not tate:  # 縦にはみ出てる
            vy *= -1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
