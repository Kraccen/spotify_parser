





def load(email, password, songs_count):
    from selenium.webdriver.chrome.options import Options
    # This blocks images and javascript requests
    chrome_prefs = {
        "profile.default_content_setting_values": {
            "images": 0
        }
    }
    # Now I just read two script files and add their text to string to use them after
    # get_token_path = r"D:\pythonProject\pythonProject\spofity_parser\get_token.js"
    # get_token_script = ''
    # with open(get_token_path, 'r') as js:
    #     for line in js:
    #         get_token_script = get_token_script + line
    #
    create_playlist_path = r"D:\pythonProject\pythonProject\spofity_parser\add_item_to_playlist.js"
    create_playlist_script = ''
    # # TODO This script is working, so I need to add all formatted links from list to this playlist
    with open(create_playlist_path, 'r') as js:
        for line in js:
            create_playlist_script = create_playlist_script + line

    # installing driver for selenium and it's options
    options = Options()

    # if True - window will be in background
    # options.headless = True

    options.add_argument("--window-size=1920,1200")

    options.experimental_options["prefs"] = chrome_prefs

    driver = webdriver.Chrome(options=options)

    with open('music.txt', 'w') as f:
        f.write('this is list of music \n')

    # get the site name and search for block with list of music
    driver.get("https://accounts.spotify.com/ru/login?continue=https%3A%2F%2Fopen.spotify.com%2F")

    # title = driver.execute_script('return document.title')
    # print(title)

    # time.sleep(10)

    # search for forms to input account info
    email_element = driver.find_element(By.ID, 'login-username')
    pass_element = driver.find_element(By.ID, 'login-password')

    # pass a keys to these forms
    email_element.send_keys(email)
    pass_element.send_keys(password)

    # get the button and click on it
    submit = driver.find_element(By.ID, 'login-button')
    submit.click()

    # just wait for loading
    waited_button = WebDriverWait(driver, 200).until(EC.presence_of_element_located((
        By.CLASS_NAME, "Z35BWOA10YGn5uc9YgAp")))

    # user_token = driver.execute_script(get_token_script)
    # print(user_token)

    # change to favorite songs page
    file = driver.get('https://open.spotify.com/collection/tracks')

    # wait until page load by checking element with class (menu of songs)
    ok = WebDriverWait(driver, 200).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'JUa6JJNj7R_Y3i4P8YUX')))

    # define action function(scroll, move)
    actions = ActionChains(driver)
    # create a playlist with top 1 user's track
    # user_playlist = driver.execute_script(create_playlist_script)
    # print(user_playlist)

    # create a js script for scrolling
    java_script = "window.scrollBy(0, 1000);"

    # using count of songs in playlist, move through all playlist
    for i in range(2, songs_count + 2):
        # because of not all elements are visible, move mouse down

        # wait until element appear, if program stuck, move mouse down
        wait_cycle = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//div[@aria-rowindex="{i}"]')))
        # search for current element in list
        song = driver.find_element(By.XPATH, f'//div[@aria-rowindex="{i}"]//a[@data-testid="internal-track-link"]')

        driver.execute_script("arguments[0].scrollIntoView();", song)
        # get the link of it
        print(song.get_attribute('href'), song.text)
        # write link into txt file
        with open('music.txt', 'a') as f:
            f.write(song.get_attribute('href') + '\n')
    return os.path.join(os.getcwd(), "music.txt")
    


# This function takes .txt file with spotify links to music, format them and makes a playlist of them and return an
# id of playlist
def format_file_to_spotify(file_path):
    print("[+] Start")
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="3adffed607c84e5bb5f34cbcef74154c",
                                                   client_secret="3b291b4ff0044a02bd43e71af9c3da42",
                                                   redirect_uri="https://translate.google.com/?sl=de&tl=en&op=translate",
                                                   scope="playlist-modify-public"
                                                   ))
    playlists = sp.current_user_playlists()
    playlist_id = ''
    playlist_url = ''
    get_link = False
    for i, item in enumerate(playlists['items']):
        if item['name'] == "My download playlist":
            print("[+] Found a same playlist, decision >>")
            answer = input('Playlist with same name exist, add music to it(y)? Or just get link?(n) (y, n) \n')
            if answer.lower() == 'y':
                print("[+] Found a same playlist, decision >> Use this playlist")
                playlist_id = item['id']
                playlist_url = item['external_urls']['spotify']
                break
            elif answer.lower() == 'n':
                print("[+] Found a same playlist, decision >> just get a link of it")
                playlist_url = item['external_urls']['spotify']
                get_link = True
                break
        else:
            user_id = sp.me()['id']
            sp.user_playlist_create(user=user_id, name="My download playlist",
                                    description="This playlist was created by SpotiFlow.py")
            playlist_id = item['id']
            playlist_url = item['external_urls']['spotify']
            break

    if get_link:
        return playlist_url
    with open(file_path, 'r') as music:
        next(music)
        for line in music:
            new_line = line.replace('https://open.', '').replace('.com/', ':').replace('/', ':').replace('spotify:track:', '')
            print(line)
            sp.playlist_add_items(playlist_id, [f'{new_line.strip()}'])
            print(f"{new_line.strip()} added to playlist")
    return playlist_url
    

if __name__ == '__main__':
    format_file_to_spotify(file_path=load(email="email", password="password", songs_count=279))