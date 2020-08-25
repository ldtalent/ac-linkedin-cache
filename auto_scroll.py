import time

REASONABLE_ITERS = 3 # to stop it from going all the way to the bottom when we don't need it, may need to increase by a bit (i.e. 5) every run 

def auto_scroll(driver):
  # Get current scroll height
  last_height = driver.execute_script("return document.body.scrollHeight")
  num_iters = 0
  while True:
    # To scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # To wait till page loads after scrolling
    time.sleep(4)
    # Scroll up a little to scroll down again because in linkedin sometimes the page stops loading the content below
    driver.execute_script("scrollBy(0,-500);")
    time.sleep(4)
    # Scroll down to bottom again
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)
    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
      break
    last_height = new_height

    num_iters += 1
    print("num_iters: ", num_iters)
    if num_iters > REASONABLE_ITERS:
      break
