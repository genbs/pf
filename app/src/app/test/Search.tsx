"use client"

import { useSearch } from "@/utils"
import React from "react"
import { Transaction } from "../types"

export default function Search({ transactions }: { transactions: Transaction[] }) {
	const [search, setSearch] = React.useState("")
	const result = useSearch(search, transactions, "description")

	return (
		<div>
			<input type="text" value={search} onChange={e => setSearch(e.target.value)} />
			<div>
				<h1>results</h1>
				{result.map(({ item, score }) => {
					return (
						<div key={item.id}>
							({score}) {item.description}
						</div>
					)
				})}
			</div>
			<div>
				<h1>transactions</h1>
				{transactions.map(transaction => {
					return <div key={transaction.id}>{transaction.description}</div>
				})}
			</div>
		</div>
	)
}
