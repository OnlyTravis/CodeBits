import os
from time import sleep
import requests
from html.parser import HTMLParser

MAX_RETRY = 2
PAUSE = 0
PAUSE_FAIL = 2

class imgSrcExtractor(HTMLParser):
	srcList: list[str] = []

	def handle_starttag(self, tag, attrs):
		if (tag == "img"):
			for attr in attrs:
				if (attr[0] != "src"): continue
				self.srcList.append(attr[1])
	
	def extract_from_link(self, src: str) -> list[str]:
		self.srcList = []
		self.feed(src)
		return self.srcList

def check_response(response: requests.Response) -> bool:
	if (response.status_code != 200): return False
	if ("fuck" in response.text): return False

	return True

def download_file(img_link: str, file_path: str) -> bool:
	"""
	return True : Downloaded successfully
	return False : Download failed
	"""
	retry = True
	retry_count = 0
	while retry:
		retry = False
		try:
			img_res = requests.get(img_link)
		except:
			print(f"An exception occured when fetching the image(Retry {retry_count})")
			retry = True
			retry_count += 1
			sleep(PAUSE_FAIL)
			return

		if not check_response(img_res):
			retry = True
			retry_count += 1

			if retry_count >= MAX_RETRY:
				print(f"File {file_path} download unsuccessful(Retry {retry_count})... Skipping.")
				sleep(PAUSE_FAIL)
				return False

			print(f"File {file_path} download unsuccessful(Retry {retry_count})... Retrying in 5 seconds.")
			sleep(PAUSE_FAIL)
			continue

		with open(file_path, "wb") as file:
			file.write(img_res.content)
			print(f"File {file_path} download successful!")
			sleep(PAUSE)
			return True

def main_procedures() -> None:
	# 1. Input
	link = input("Enter url to extract from : ")
	img_name = input("Enter image name(default=img) : ")
	if (img_name.strip() == ""):
		img_name = "img"

	# 2. Get HTML text
	res = requests.get(link)
	if (res.status_code != 200):
		print("Responce's status code is not 200!")
		print("Contents : ")
		print(res.content)
		return

	# 3. Parse HTML & get img srcs
	parser = imgSrcExtractor()
	img_links = parser.extract_from_link(res.text)

	# 4. Prepare output directory
	'''
	os.makedirs("./outputs", exist_ok=True)
	outputDirs = os.listdir("./outputs")
	output_num = 1
	while (f"output{output_num}" in outputDirs):
		output_num += 1
	output_dir = f"./outputs/output{output_num}"
	os.makedirs(output_dir)'''
	
	output_dir = f"./outputs/{img_name}"
	os.makedirs(output_dir)

	# 5. Downlaod each image
	failed_list: list[str] = []
	for i, img_link in enumerate(img_links):
		if (not download_file(img_link, f"{output_dir}/{img_name}_{i+1:0>3d}.jpeg")):
			failed_list.append(f"{output_dir}/{img_name}_{i+1:0>3d}.jpeg")

	if (len(failed_list) != 0):
		with open(f"{output_dir}/failed_list.txt", "w") as file:
			file.write("\n".join(failed_list))

def main() -> None:
	loop = True
	while loop:
		loop = False
		main_procedures()
		res = input("Extraction finished! Go for another one ?(Y/N) ").lower()
		if (res in ["y", "yes"]):
			loop = True


if __name__ == "__main__":
	main()