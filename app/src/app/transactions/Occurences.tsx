"use client"

import { Slider } from "@mui/material"
import { Prisma } from "@prisma/client"

import Fuse from "fuse.js"
import React from "react"
import TransactionModal from "../components/TransactionModal"

export default function Occurrences({ transactions }: { transactions: Prisma.$TransactionsPayload["scalars"][] }) {
	// voglio sapere le spese mensili riccorenti, per ogni transazione vedere la descrizione e contare quante volte compare nei mesi
	const [threshold, setThreshold] = React.useState(0.1)
	const [occurrences, setOccurrences] = React.useState<{ ids: number[]; count: number; description: string }[]>([])
	const fuse = React.useMemo(
		() =>
			new Fuse(transactions, {
				keys: ["description"],
				threshold,
				isCaseSensitive: false,
			}),
		[transactions, threshold]
	)

	if (typeof window === "undefined") return

	//@ts-ignore
	React.useEffect(() => {
		// const occurrences: Record<string, { ids: number[]; count: number }> = {}
		// transactions.forEach(transaction => {
		// 	const results = fuse.search(transaction.description || "")
		// 	if (!results.length) return
		// 	const key = results[0].item.description || ""
		// 	if (!occurrences[key]) occurrences[key] = { ids: [], count: 0 }
		// 	occurrences[key].ids.push(transaction.id)
		// 	occurrences[key].count++
		// })
		// const sorted = Object.entries(occurrences)
		// 	.map(([description, { ids, count }]) => ({ description, ids, count }))
		// 	.sort((a, b) => b.count - a.count)
		// setOccurrences(sorted)
	}, [transactions, fuse, threshold])

	return (
		<div>
			<Slider min={0} max={1} step={0.01} value={threshold} onChange={(_, v) => setThreshold(v as number)} />

			{occurrences.map(({ ids, count, description }) => (
				<div key={description}>
					<h3>{description}</h3>
					<p>
						{ids.map(id => {
							const transaction = transactions.find(transaction => transaction.id === id)
							return transaction ? <TransactionModal key={id} transaction={transaction} /> : id
						})}
					</p>
					<p>{count}</p>
				</div>
			))}
		</div>
	)
}
