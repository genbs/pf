import Fuse from "fuse.js"
import React from "react"

export function createSearch<T>(items: T[], keys: (keyof T)[]) {
	const fuse = new Fuse(items, {
		keys: keys as string[],
		threshold: 0.1,
		isCaseSensitive: false,
		includeScore: true,
		useExtendedSearch: true,
		// @ts-ignore
		getFn: (obj: any, path: string): string | string[] => {
			return [obj[path], ...obj[path].split(" ")]
		},
	})

	function searchFn(query: string) {
		return fuse.search(query)
	}
	searchFn.items = items

	return searchFn
}

export function useSearch(input: string, items: any[], keys: string[]) {
	const workerRef = React.useRef<Worker>()

	const [result, setResult] = React.useState<{ item: any; score: number }[]>([])

	React.useEffect(() => {
		workerRef.current = new Worker(new URL("./transactionsSearchWorker.ts", import.meta.url))

		return () => {
			workerRef.current?.terminate()
		}
	}, [])

	React.useEffect(() => {
		if (!workerRef.current) return

		workerRef.current.postMessage(JSON.stringify({ event: "createSearch", data: { items, keys } }))

		function handleCreateSearchResult(e: MessageEvent) {
			const { event } = JSON.parse(e.data)

			switch (event) {
				case "createSearchResult":
					break
			}
		}

		workerRef.current.addEventListener("message", handleCreateSearchResult)

		return () => {
			workerRef.current?.removeEventListener("message", handleCreateSearchResult)
		}
	}, [workerRef, items, keys])

	React.useEffect(() => {
		if (!workerRef.current || input.length < 2) return

		function handleSearchResult(e: MessageEvent) {
			const { event, data } = JSON.parse(e.data)
			switch (event) {
				case "searchResult":
					setResult(data)
					break
			}
		}

		workerRef.current.addEventListener("message", handleSearchResult)

		workerRef.current?.postMessage(JSON.stringify({ event: "search", data: { query: input } }))

		return () => {
			workerRef.current?.removeEventListener("message", handleSearchResult)
		}
	}, [workerRef, input])

	return result
}
