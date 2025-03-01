import os
from time import sleep
import requests
from html.parser import HTMLParser

MAX_RETRY = 2

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

def download_file(img_link: str, file_path: str) -> None:
	retry = True
	retry_count = 0
	while retry:
		retry = False
		img_res = requests.get(img_link)

		if not check_response(img_res):
			retry = True
			retry_count += 1

			if retry_count > MAX_RETRY:
				print(f"Maximum retry reached! Skipping {file_path}...")
				sleep(5)
				return

			print(f"File {file_path} download unsuccessful(Retry {retry_count})... Retrying in 5 seconds.")
			sleep(5)
			continue

		with open(file_path, "wb") as file:
			file.write(img_res.content)
			print(f"File {file_path} download successful!")
			sleep(1)

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
	outputDirs = os.listdir("./outputs")
	output_num = 1
	while (f"output{output_num}" in outputDirs):
		output_num += 1
	output_dir = f"./outputs/output{output_num}"
	os.makedirs(output_dir)

	# 5. Downlaod each image
	for i, img_link in enumerate(img_links):
		download_file(img_link, f"{output_dir}/{img_name}_{i+1:0>3d}.jpeg")

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