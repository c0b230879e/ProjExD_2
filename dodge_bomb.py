import os
import random
import sys
import time
import pygame as pg

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


def game_over(screen: pg.Surface) -> None:
    """
    gameover画面を表示する関数
    引数: screen
    戻り値: なし
    """
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


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    爆弾の画像リストと加速度リストを返す
    """
    accs = [a for a in range(1, 11)] 
    bb_imgs = []  
    for r in range(1, 11): 
        bb_img = pg.Surface((20 * r, 20 * r), pg.SRCALPHA)
        pg.draw.circle(bb_img, (255, 0, 0, 255), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img) 
    return bb_imgs, accs


def generate_kk_images(base_img: pg.Surface) -> dict[tuple[int, int], pg.Surface]:
    """
    押下キーに対応する移動量タプルをキーに、rotozoomしたSurfaceを値とする辞書
    """
    directions = {
        (0, 0): 0,      # 静止
        (0, -1): -90,   # 上
        (0, 1): 90,     # 下
        (-1, 0): 180,   # 左
        (1, 0): 0,      # 右
        (-1, -1): -135, # 左上
        (-1, 1): 135,   # 左下
        (1, -1): -45,   # 右上
        (1, 1): 45,     # 右下
    }

    images = {}
    for (dx, dy), angle in directions.items():
        rotated_img = pg.transform.rotozoom(base_img, angle, 1.0)
        images[(dx, dy)] = rotated_img
    return images


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_base_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)

    # 移動量と回転済み画像の辞書を作成
    kk_images = generate_kk_images(kk_base_img)
    kk_rct = kk_base_img.get_rect()
    kk_rct.center = 300, 200

    # 爆弾画像リストと加速度リストを初期化
    bb_imgs, saccs = init_bb_imgs()
    bb_img = bb_imgs[0]  # 初期状態の爆弾画像
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)

    vx, vy = +5, +5  # 初期速度ベクトル
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
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]
        
        # 移動量に対応する方向画像を取得
        direction = (sum_mv[0] // abs(sum_mv[0]) if sum_mv[0] != 0 else 0,
                     sum_mv[1] // abs(sum_mv[1]) if sum_mv[1] != 0 else 0)
        kk_img = kk_images.get(direction, kk_images[(0, 0)])  
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        # タイマーに応じた速度更新
        level = min(tmr // 500, 9)  # 爆弾レベルを0から9の範囲で制限
        vx = 5 * saccs[level] * (1 if vx > 0 else -1)  # 現在の加速度に基づいて速度更新
        vy = 5 * saccs[level] * (1 if vy > 0 else -1)

        # 爆弾画像の切り替え
        bb_img = bb_imgs[level]
        bb_rct = bb_img.get_rect(center=bb_rct.center)

        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
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
