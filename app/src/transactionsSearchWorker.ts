import Fuse from "fuse.js"

let fuse: Fuse<any>

addEventListener("message", async e => {
	const { event, data } = JSON.parse(e.data)

	switch (event) {
		case "createSearch":
			const { items, key } = data
			postMessage(JSON.stringify({ event: "createSearchStart", data: items.length }))

			fuse = new Fuse(items, {
				keys: [key],
				threshold: 0.1,
				isCaseSensitive: false,
				includeScore: true,
				useExtendedSearch: true,
				// @ts-ignore
				getFn: (obj: any, path: string): string | string[] => {
					return [obj[path], ...obj[path].split(" ")]
				},
			})

			postMessage(JSON.stringify({ event: "createSearchResult", data: items.length }))

			break
		case "search":
			const { query } = data

			const results = fuse.search(query)

			postMessage(JSON.stringify({ event: "searchResult", data: results }))

			break
	}
})
