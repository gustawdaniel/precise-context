<script setup>
const { data, pending, error, refresh } = await useFetch('/api/leads')
const search = ref('')
const selectedScore = ref(0)
const selectedTag = ref([])

const sorting = ref([{ id: 'score', desc: true }])

const columns = [{
  accessorKey: 'name',
  header: 'Analyzed profile',
}, {
  accessorKey: 'score',
  header: 'Score',
  sortable: true,
}, {
  accessorKey: 'tags',
  header: 'Tags',
}, {
  id: 'action',
  header: 'Actions',
}]

const leads = computed(() => (data.value?.leads || []).map(lead => {
  // Safe defaults for unstructured/failed analysis
  const analysis = lead.analysis || {}
  return {
    ...lead,
    analysis: {
      ...analysis,
      scores: analysis.scores || { role_fit: 0, engagement: 0, technical_needs: 0 },
      tags: analysis.tags || [],
      qualitative: analysis.qualitative || {
        role_description: 'N/A',
        personality_profile: 'N/A',
        key_information: analysis.raw_content ? 'Raw Analysis: ' + analysis.raw_content : 'No analysis available'
      },
      engaging_reply: analysis.engaging_reply || 'No draft reply available.'
    }
  }
}))

const filteredLeads = computed(() => {
  let result = leads.value.filter(lead => {
    const matchesSearch = !search.value ||
      lead.name.toLowerCase().includes(search.value.toLowerCase()) ||
      lead.phone.includes(search.value) ||
      (lead.analysis.qualitative.role_description && lead.analysis.qualitative.role_description.toLowerCase().includes(search.value.toLowerCase()))

    const matchesScore = lead.analysis.scores.role_fit >= selectedScore.value

    // Multi-tag check (if NO tags selected, show all. If tags selected, show if lead has ANY of them)
    const matchesTag = selectedTag.value.length === 0 ||
      selectedTag.value.some(t => lead.analysis.tags.includes(t))

    return matchesSearch && matchesScore && matchesTag
  })

  // Apply sorting
  if (sorting.value.length > 0) {
    const sort = sorting.value[0]
    result.sort((a, b) => {
      let valA, valB
      if (sort.id === 'score') {
        valA = a.analysis.scores.role_fit
        valB = b.analysis.scores.role_fit
      } else {
        // Fallback for other potential columns, though primarily sorting by score
        valA = a[sort.id]
        valB = b[sort.id]
      }

      if (valA < valB) return sort.desc ? 1 : -1
      if (valA > valB) return sort.desc ? -1 : 1
      return 0
    })
  }

  return result
})




const selectedLead = ref(null)
const isOpen = ref(false)

function openDetails(lead) {
  selectedLead.value = lead
  isOpen.value = true
}

function copyReply(text) {
  navigator.clipboard.writeText(text)
  alert('Draft reply copied to clipboard!')
}

// Extraction unique tags
const allTags = computed(() => {
  const tags = new Set()
  leads.value.forEach(l => l.analysis.tags.forEach(t => tags.add(t)))
  return Array.from(tags).map(t => ({ label: t, value: t }))
})


</script>

<template>
  <div class="min-h-screen bg-gray-950 text-gray-100 font-sans selection:bg-primary-500/30">
    <div
      class="fixed inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary-900/20 via-gray-950 to-gray-950 pointer-events-none z-0">
    </div>

    <!-- Navbar -->
    <div class="border-b border-white/5 bg-gray-900/60 backdrop-blur-xl sticky top-0 z-50">
      <div class="container mx-auto px-6 py-4 flex justify-between items-center relative">
        <div class="flex items-center gap-4">
          <div
            class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-indigo-600 shadow-lg shadow-primary-500/20 flex items-center justify-center">
            <span class="text-white font-bold text-lg">P</span>
          </div>
          <div>
            <h1 class="text-lg font-semibold text-white tracking-tight">Protocol Cloud</h1>
            <div class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span class="text-xs text-gray-400 font-medium tracking-wide">LIVE DASHBOARD</span>
            </div>
          </div>
        </div>
        <div class="flex gap-6 text-sm">
          <div class="flex flex-col items-end">
            <span class="text-xs text-gray-500 font-medium uppercase tracking-wider">Total Leads</span>
            <span class="text-white font-bold">{{ leads.length }}</span>
          </div>
          <div class="flex flex-col items-end">
            <span class="text-xs text-gray-500 font-medium uppercase tracking-wider">Filtered</span>
            <span class="text-primary-400 font-bold">{{ filteredLeads.length }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mx-auto px-6 py-8 relative z-10">

      <!-- Filters Card -->
      <div class="bg-gray-900/40 border border-white/5 backdrop-blur-md rounded-2xl p-1 mb-8 shadow-xl">
        <div class="flex flex-col md:flex-row gap-4 p-4 items-center">
          <div class="relative flex-grow group">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <UIcon name="i-heroicons-magnifying-glass-20-solid"
                class="text-gray-500 group-focus-within:text-primary-400 transition-colors" />
            </div>
            <input v-model="search" type="text" placeholder="Search leads..."
              class="w-full bg-gray-950/50 text-white placeholder-gray-500 text-sm rounded-xl border-0 ring-1 ring-white/10 focus:ring-2 focus:ring-primary-500/50 py-2.5 pl-10 transition-all" />
          </div>

          <div class="w-full md:w-64">
            <USelectMenu v-model="selectedTag" :items="allTags" value-key="value" multiple placeholder="Filter by Tag"
              :ui="{
                color: { gray: { outline: 'bg-gray-950/50 ring-white/10 text-white focus:ring-primary-500/50' } }
              }" />
          </div>

          <div class="flex items-center gap-4 bg-gray-950/50 px-4 py-2 rounded-xl ring-1 ring-white/10 min-w-[240px]">
            <span class="text-xs text-gray-400 font-bold uppercase tracking-wider whitespace-nowrap">Fit > {{
              selectedScore }}%</span>
            <USlider v-model="selectedScore" :min="0" :max="100" size="sm" color="primary" class="flex-grow" />
          </div>
        </div>
      </div>

      <!-- Table View -->
      <UCard :ui="{
        background: 'bg-gray-900/40 backdrop-blur-sm',
        ring: 'ring-1 ring-white/5',
        divide: 'divide-white/5',
        header: { padding: 'p-0' },
        body: { padding: 'p-0' }
      }">
        <UTable v-model:sorting="sorting" :data="filteredLeads" :columns="columns" :loading="pending" :ui="{
          th: { base: 'uppercase text-xs font-bold text-gray-500 tracking-wider py-4 bg-gray-950/30' },
          td: { base: 'py-4 text-gray-300' },
          tr: { base: 'hover:bg-white/[0.02] transition-colors' }
        }">
          <template #name-cell="{ row }">
            <div class="flex flex-col cursor-pointer group" @click="openDetails(row.original)">
              <span class="font-semibold text-white group-hover:text-primary-400 transition-colors">{{ row.original.name
              }}</span>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-xs text-gray-500 font-mono bg-gray-950 px-1.5 rounded">{{ row.original.phone }}</span>
              </div>
              <p class="text-sm text-gray-400 mt-2 line-clamp-1 italic border-l-2 border-primary-500/30 pl-2">
                {{ row.original.analysis.qualitative.role_description }}
              </p>
            </div>
          </template>

          <template #score-cell="{ row }">
            <div class="flex items-center gap-3">
              <div class="relative w-12 h-12 flex items-center justify-center">
                <svg class="w-full h-full -rotate-90" viewBox="0 0 36 36">
                  <path class="text-gray-800"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none"
                    stroke="currentColor" stroke-width="3" />
                  <path :class="row.original.analysis.scores.role_fit > 70 ? 'text-primary-500' : 'text-gray-600'"
                    :stroke-dasharray="`${row.original.analysis.scores.role_fit}, 100`"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none"
                    stroke="currentColor" stroke-width="3" />
                </svg>
                <span class="absolute text-xs font-bold text-white">{{ row.original.analysis.scores.role_fit }}</span>
              </div>
            </div>
          </template>

          <template #tags-cell="{ row }">
            <div class="flex gap-1.5 flex-wrap max-w-xs">
              <span v-for="tag in row.original.analysis.tags" :key="tag"
                class="px-2 py-0.5 rounded-md text-[10px] font-medium uppercase tracking-wide bg-gray-800 text-gray-300 border border-white/5">
                {{ tag }}
              </span>
            </div>
          </template>

          <template #action-cell="{ row }">
            <div class="flex gap-2 justify-end pr-4">
              <UButton color="gray" variant="ghost" icon="i-heroicons-eye-20-solid"
                class="hover:bg-primary-500/10 hover:text-primary-400" @click="openDetails(row.original)" />
              <UButton color="gray" variant="ghost" icon="i-heroicons-clipboard-document-20-solid"
                class="hover:bg-emerald-500/10 hover:text-emerald-400"
                @click="copyReply(row.original.analysis.engaging_reply)" />
            </div>
          </template>

        </UTable>
      </UCard>
    </div>

    <!-- Details Slideover -->
    <USlideover v-model="isOpen"
      :ui="{ width: 'max-w-xl', background: 'bg-gray-900', overlay: { background: 'backdrop-blur-sm' } }">
      <div class="flex flex-col h-full bg-gray-900 border-l border-white/10" v-if="selectedLead">

        <!-- Header -->
        <div class="p-6 border-b border-white/5 bg-gray-900 sticky top-0 z-20">
          <div class="flex justify-between items-start">
            <div>
              <h2 class="text-2xl font-bold text-white tracking-tight">{{ selectedLead.name }}</h2>
              <div class="text-gray-400 font-mono text-sm mt-1">{{ selectedLead.phone }}</div>
            </div>
            <UButton icon="i-heroicons-x-mark-20-solid" color="gray" variant="ghost" @click="isOpen = false" />
          </div>
        </div>

        <div class="p-6 flex-1 overflow-y-auto space-y-8">
          <!-- Scores Grid -->
          <div class="grid grid-cols-3 gap-4">
            <div class="bg-gray-950/50 p-4 rounded-xl border border-white/5 flex flex-col items-center">
              <div class="text-[10px] text-gray-500 uppercase font-bold tracking-widest mb-1">Role Fit</div>
              <div
                class="text-3xl font-bold bg-gradient-to-br from-primary-400 to-primary-600 bg-clip-text text-transparent">
                {{ selectedLead.analysis.scores.role_fit }}%</div>
            </div>
            <div class="bg-gray-950/50 p-4 rounded-xl border border-white/5 flex flex-col items-center">
              <div class="text-[10px] text-gray-500 uppercase font-bold tracking-widest mb-1">Engagement</div>
              <div class="text-3xl font-bold text-blue-400">{{ selectedLead.analysis.scores.engagement }}%</div>
            </div>
            <div class="bg-gray-950/50 p-4 rounded-xl border border-white/5 flex flex-col items-center">
              <div class="text-[10px] text-gray-500 uppercase font-bold tracking-widest mb-1">Tech Needs</div>
              <div class="text-3xl font-bold text-emerald-400">{{ selectedLead.analysis.scores.technical_needs }}%</div>
            </div>
          </div>

          <!-- Profile Cards -->
          <div class="space-y-4">
            <div class="bg-gray-800/20 p-5 rounded-2xl border border-white/5">
              <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                <UIcon name="i-heroicons-user-20-solid" /> Role Description
              </h3>
              <p class="text-gray-300 leading-relaxed">{{ selectedLead.analysis.qualitative.role_description }}</p>
            </div>

            <div class="bg-gray-800/20 p-5 rounded-2xl border border-white/5">
              <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                <UIcon name="i-heroicons-sparkles-20-solid" /> Personality
              </h3>
              <p class="text-gray-300 leading-relaxed">{{ selectedLead.analysis.qualitative.personality_profile }}
              </p>
            </div>

            <div class="bg-gray-800/20 p-5 rounded-2xl border border-white/5">
              <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                <UIcon name="i-heroicons-key-20-solid" /> Key Info
              </h3>
              <p class="text-gray-300 leading-relaxed">{{ selectedLead.analysis.qualitative.key_information }}</p>
            </div>
          </div>

          <!-- Draft Reply -->
          <div class="relative group">
            <div
              class="absolute -inset-0.5 bg-gradient-to-r from-primary-500 to-indigo-500 rounded-2xl opacity-20 group-hover:opacity-40 transition duration-500 blur">
            </div>
            <div class="relative bg-gray-900 border border-white/10 p-5 rounded-2xl">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-xs font-bold text-primary-400 uppercase tracking-widest flex items-center gap-2">
                  <UIcon name="i-heroicons-chat-bubble-left-right-20-solid" /> Suggested Reply
                </h3>
                <UButton size="xs" icon="i-heroicons-clipboard-document-20-solid" variant="soft" color="primary"
                  @click="copyReply(selectedLead.analysis.engaging_reply)">Copy</UButton>
              </div>
              <div class="text-lg text-white font-medium italic font-serif leading-relaxed">
                "{{ selectedLead.analysis.engaging_reply }}"
              </div>
            </div>
          </div>

          <!-- Messages -->
          <div>
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-6">Chat History</h3>
            <div
              class="space-y-6 relative before:absolute before:inset-y-0 before:left-4 before:w-px before:bg-white/5">
              <div v-for="(msg, index) in selectedLead.messages" :key="index" class="relative pl-12 group">
                <!-- Timeline dot -->
                <div class="absolute left-[13px] top-3 w-2.5 h-2.5 rounded-full border-2 border-gray-900"
                  :class="msg.type === 'out' ? 'bg-primary-500' : 'bg-gray-600'"></div>

                <div class="mb-1 flex items-center gap-2">
                  <span class="text-xs font-bold" :class="msg.type === 'out' ? 'text-primary-400' : 'text-gray-300'">
                    {{ msg.type === 'out' ? 'You' : selectedLead.name }}
                  </span>
                  <span class="text-[10px] text-gray-600">
                    {{ new Date(msg.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
                  </span>
                </div>

                <div class="p-3 rounded-tr-2xl rounded-bl-2xl rounded-br-2xl text-sm leading-relaxed"
                  :class="msg.type === 'out' ? 'bg-primary-500/10 text-primary-100' : 'bg-gray-800 text-gray-300'">
                  {{ msg.message }}
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </USlideover>

  </div>
</template>
