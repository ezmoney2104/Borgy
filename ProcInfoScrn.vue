<template>
  <v-container fluid>
    <v-row>
      <v-col v-show="currentComponent === 'ProcessChart'" class="mb-13"
        ><ProcessChart
          :incremented-units="incrementedUnits"
          :non-defective-products="nonDefectiveProducts"
          :working-rate="workingRate"
          :operationInformation="operation_table"
      /></v-col>
      <v-col v-show="currentComponent === 'ErrorInformation'"
        ><error-information :abnormalities="abnormalitiesData"></error-information
      ></v-col>
    </v-row>

    <v-row
      ><v-col><replenishment-notice :notice="replenishmentData"></replenishment-notice></v-col
    ></v-row>
  </v-container>
</template>

<script>
import ProcessChart from '@/components/pages/ProcessInformationScreen/ProcessChart.vue'
import ReplenishmentNotice from '@/components/pages/ProcessInformationScreen/ReplenishmentNotice.vue'
import { FetchAPI } from '@/utility/apiRequest'
import ErrorInformation from '@/components/pages/ProcessInformationScreen/ErrorInformation.vue'

export default {
  name: 'ProcessInformationScreen',
  components: {
    ProcessChart,
    ReplenishmentNotice,
    ErrorInformation,
  },
  data() {
    return {
      referenceCT: 0,
      operationInformation: [],
      incrementedUnits: 0,
      incrementInterval: null,
      nonDefectiveProducts: 0,
      workingRate: 0,
      operation_table: [],
      replenishmentData: [],
      abnormalitiesData: [],
      currentComponent: 'ProcessChart',
    }
  },
  async mounted() {
    await this.setOperationsData()
    await this.setReferenceCT()
    await this.setAbnormalitiesData()
    await this.setReplenishmentData()

    this.startSwitchInterval()
  },
  methods: {
    /**
     * Starts the interval to toggle between ProcessChart and Abnormalitues
     */
    startSwitchInterval() {
      const intervals = [
        { component: 'ProcessChart', duration: 7000 },
        { component: 'ErrorInformation', duration: 7000 },
      ]

      let index = 0
      const switchComponent = () => {
        this.currentComponent = intervals[index].component
        setTimeout(() => {
          index = (index + 1) % intervals.length
          switchComponent()
        }, intervals[index].duration)
      }

      switchComponent()
    },
    /**
     * Retrieves all operation information
     * @returns {array} retrieved data
     */
    async fetchAllOperations() {
      try {
        const api = new FetchAPI()
        const response = await api.get('/api/get-all-operations')
        return [...response.data]
      } catch (error) {
        console.log(error)
      }
    },

    /**
     * Assign the data to global variables operationInformation and nonDefectiveProducts
     */
    async setOperationsData() {
      this.operationInformation = await this.fetchAllOperations()
      await this.setNonDefectiveProducts()
    },
    /**
     * Assign data for non-defective products
     */
    async setNonDefectiveProducts() {
      const lastData = this.operationInformation?.at(-1)

      this.nonDefectiveProducts = lastData?.non_defective_products
      this.initializeIncrementer()
      this.getOperationTable()
    },
    /**
     * Retrieves data from the replenishment notice table
     * @returns {array} retrieved data
     */
    async fetchReplenishmentNotice() {
      try {
        const api = new FetchAPI()
        const response = await api.get('/api/get-replenishment-notice')
        return [...response.data]
      } catch (error) {
        console.log(error)
      }
    },
    /**
     * Assign replenishment data to global variable replenishmentData
     */
    async setReplenishmentData() {
      this.replenishmentData = await this.fetchReplenishmentNotice()
    },
    /**
     * Retrieves all Abnormalities
     * @returns {array} abnormalities array data
     */
    async fetchAbnormalities() {
      try {
        const api = new FetchAPI()
        const response = await api.get('/api/get-abnormalities')
        return [...response.data]
      } catch (error) {
        console.log(error)
      }
    },
    /**
     * Assign the fetched abnormalities data to global variable abnormalitiesData
     */
    async setAbnormalitiesData() {
      this.abnormalitiesData = await this.fetchAbnormalities()
    },
    /**
     * Retrieves the reference cycle time
     * @returns {number} retrieved data
     */
    async fetchReferenceCT() {
      try {
        const api = new FetchAPI()
        const response = await api.get('/api/get-ref-cycle-time')

        return response.data[0].reference_cycle_time
      } catch (error) {
        console.log(error)
      }
    },
    /**
     * Assign data to global variable referenceCT
     */
    async setReferenceCT() {
      let ref_CT = await this.fetchReferenceCT()

      this.referenceCT = ref_CT * 1000 || 2000
      this.startIncrementer()
    },
    /**
     * Updates the planned number of units
     */
    async updatePlannedUnits() {
      try {
        const api = new FetchAPI()
        const lastOperation = this.operationInformation?.at(-1)

        if (lastOperation) {
          const processId = lastOperation.process_id
          const payload = { planned_number_units: this.incrementedUnits }

          await api.put(`/api/update-units/${processId}`, payload)
        }
      } catch (error) {
        console.error('Failed to update planned number units:', error)
      }
    },
    /**
     * Assign the value of global variable incrementedUnits and initialize the increment function
     */
    initializeIncrementer() {
      if (this.operationInformation?.length > 0) {
        const lastItem = this.operationInformation.at(-1)

        this.incrementedUnits = lastItem.planned_number_units || 0
        this.startIncrementer()
      }
    },
    /**
     * Starts incrementing the planned units and work time rate
     */
    startIncrementer() {
      this.clearIncrementer()
      const condition = this.operationInformation?.length > 0 && this.referenceCT !== 0

      this.incrementInterval = setInterval(async () => {
        if (condition) {
          this.incrementedUnits += 1
        }
        await this.updatePlannedUnits()
        await this.calculateWorkingTime()
      }, this.referenceCT)
    },

    /**
     * Resets the interval value
     */
    clearIncrementer() {
      if (this.incrementInterval) {
        clearInterval(this.incrementInterval)
      }
    },
    /**
     * Calculate the working
     */
    async calculateWorkingTime() {
      this.workingRate = +((this.nonDefectiveProducts / this.incrementedUnits) * 100).toFixed(2)
    },
    /**
     * Function use for getting product number format
     * @returns {string} new formatted  product number
     */
    formatProductNumber(number) {
      const defaultFill = '0000'

      if (String(number).length === 5) {
        return '9999'
      }
      return (defaultFill + number).substr(-4)
    },

    /**
     * Maps through the operationInformation array and creates new object
     */
    getOperationTable() {
      const operationInformation = this.operationInformation
      const operationInformation_map = operationInformation?.map(
        (filObj) =>
          new Object({
            process_id: filObj.process_id,
            process_name: filObj.process_name,
            product_number: this.formatProductNumber(filObj.product_number),
            facility_cycle_time: filObj.facility_cycle_time.toFixed(2),
          }),
      )

      this.operation_table = operationInformation_map
    },
  },
}
</script>
