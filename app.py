import threading
import time
import requests
import flet as ft

def main(page: ft.Page):
    page.title = "Panel Sterowania - Darts"
    page.bgcolor = "#0d1a2d"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    txt_format = ft.TextField(label="Format Meczowy", hint_text="np. First to 8 Legs", bgcolor="#08101c", color="#fff", border_color="#1a365d")
    txt_p1 = ft.TextField(label="Gracz 1 Nazwa", hint_text="np. Peter Wright (SCO)", bgcolor="#08101c", color="#fff", border_color="#1a365d", expand=True)
    txt_p2 = ft.TextField(label="Gracz 2 Nazwa", hint_text="np. Luke Littler (ENG)", bgcolor="#08101c", color="#fff", border_color="#1a365d", expand=True)
    txt_stage = ft.TextField(label="Runda / Faza", hint_text="np. Final", bgcolor="#08101c", color="#fff", border_color="#1a365d", expand=True)
    txt_subtext = ft.TextField(label="Podtytuł / Turniej", hint_text="np. Mistrzostwa Polski", bgcolor="#08101c", color="#fff", border_color="#1a365d", expand=True)

    lbl_turn = ft.Text("Rzuca: -", size=16, weight=ft.FontWeight.BOLD, color="#e6235c")
    lbl_legs = ft.Text("P1 Legi: 0 | P2 Legi: 0", size=16, weight=ft.FontWeight.BOLD, color="#fff")
    txt_custom = ft.TextField(label="Wpisz punkty z tury", keyboard_type=ft.KeyboardType.NUMBER, bgcolor="#08101c", color="#fff", border_color="#1a365d", expand=True)

    def send_action(endpoint, data={}):
        try:
            requests.post(f"http://127.0.0.1:5000{endpoint}", json=data)
            update_state()
        except Exception:
            pass

    def save_settings(e):
        send_action("/update_match", {
            "format": txt_format.value,
            "stage": txt_stage.value,
            "subtext": txt_subtext.value,
            "p1_name": txt_p1.value,
            "p2_name": txt_p2.value
        })

    def submit_pts(pts):
        send_action("/score_visit", {"points": pts})

    def submit_custom(e):
        if txt_custom.value.isdigit():
            submit_pts(int(txt_custom.value))
            txt_custom.value = ""
            txt_custom.update()

    def do_undo(e):
        send_action("/undo")

    def do_reset(e):
        send_action("/reset_match")

    def update_state():
        try:
            res = requests.get("http://127.0.0.1:5000/get_state")
            st = res.json()
            t_name = (st["player1"]["name"] if st["turn"] == 1 else st["player2"]["name"]) or "Gracz"
            lbl_turn.value = f"Rzuca: {t_name}"
            lbl_legs.value = f"P1 Legi: {st['player1']['legs']} | P2 Legi: {st['player2']['legs']}"
            page.update()
        except Exception:
            pass

    page.add(
        ft.Text("🎯 Panel Sterowania - Darts", size=22, weight=ft.FontWeight.BOLD, color="#00d4ff"),
        ft.Container(
            content=ft.Column([
                txt_format,
                ft.Row([txt_p1, txt_p2]),
                ft.Row([txt_stage, txt_subtext]),
                ft.ElevatedButton("Zapisz ustawienia", on_click=save_settings, bgcolor="#00d4ff", color="#000")
            ]),
            bgcolor="#102038", padding=15, border_radius=6, border=ft.border.all(1, "#1a365d")
        ),
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([lbl_turn, lbl_legs], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor="#08101c", padding=12, border_radius=4, border=ft.border.all(1, "#1a365d")
                ),
                ft.Row([txt_custom, ft.ElevatedButton("Zatwierdź", on_click=submit_custom, bgcolor="#00d4ff", color="#000")]),
                ft.Text("Szybkie przyciski:", size=13, weight=ft.FontWeight.BOLD, color="#8fa3c7"),
                ft.ResponsiveRow([
                    ft.Container(ft.ElevatedButton(str(p), on_click=lambda e, pts=p: submit_pts(pts), bgcolor="#152a4a", color="#fff", width=70), col=2)
                    for p in [180, 140, 100, 85, 81, 60, 45, 41, 26, 0]
                ])
            ]),
            bgcolor="#102038", padding=15, border_radius=6, border=ft.border.all(1, "#1a365d"), margin=ft.margin.symmetric(vertical=15)
        ),
        ft.Row([
            ft.ElevatedButton("↩ Cofnij", on_click=do_undo, bgcolor="#8b1e3f", color="#fff", expand=True),
            ft.ElevatedButton("🔄 Reset", on_click=do_reset, bgcolor="#8b1e3f", color="#fff", expand=True)
        ]),
        ft.Container(
            content=ft.Text("Link do OBS: http://127.0.0.1:5000/scoreboard", size=13, color="#8fa3c7", text_align=ft.TextAlign.CENTER),
            bgcolor="#08101c", padding=10, border_radius=4, border=ft.border.all(1, "#1a365d"), margin=ft.margin.only(top=15)
        )
    )

    def background_poll():
        while True:
            time.sleep(0.5)
            try:
                update_state()
            except Exception:
                pass

if __name__ == '__main__':
    # Odpalamy pętlę w tle jako wątek daemon, żeby nie blokowała Fleta
    t = threading.Thread(target=background_poll, daemon=True)
    t.start()
    
    # Startujemy apkę Fleta
    ft.app(target=main)
