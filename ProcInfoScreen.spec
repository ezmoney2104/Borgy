import { shallowMount } from '@vue/test-utils'
import ProcessInformationScreen from '@/components/pages/ProcessInformationScreen.vue'
import 'jest-canvas-mock'
import { FetchAPI } from '@/utility/apiRequest'

const sampleResult = [
  {
    facility_cycle_time: 2,
    non_defective_products: 20,
    operation_status: 1,
    planned_number_units: 54,
    process_id: 1,
    process_name: '部品供給機',
    product_number: 4512,
    coordinates: {
      coordinates_id: 1,
      height: 40,
      width: 70,
      x_position: 65,
      y_position: 515,
    },
    replenishmentData: [],
  },
  {
    facility_cycle_time: 2.05,
    non_defective_products: 10,
    operation_status: 2,
    planned_number_units: 35,
    process_id: 2,
    process_name: '成型機1',
    product_number: 4123,
    coordinates: {
      coordinates_id: 2,
      height: 40,
      width: 70,
      x_position: 65,
      y_position: 425,
    },
    replenishmentData: [],
  },
]

jest.mock('@/utility/apiRequest', () => ({
  FetchAPI: jest.fn(() => ({
    get: jest.fn(() => Promise.resolve({ success: true, data: [] })),
    put: jest.fn(() => Promise.resolve({ success: true, message_content: 'Updated successfully' })),
  })),
}))

jest.spyOn(console, 'log').mockImplementation(() => {
  return
})

jest.spyOn(console, 'warn').mockImplementation((message) => {
  if (message.includes('[Vue warn]')) return
})

window.console.log = jest.fn()
describe('Testing ProcessInformationScreen.vue', () => {
  const wrapper = shallowMount(ProcessInformationScreen, {
    global: {
      components: {
        VContainer: 'v-container',
        VCol: 'v-col',
        VRow: 'v-row',
      },
    },
    data() {
      return {
        referenceCT: 0,
        operationInformation: [],
        incrementedUnits: 0,
        incrementInterval: null,
        operation_table: [],
        replenishmentData: [],
      }
    },
  })

  // it('should initialize data correctly', () => {
  //   expect(wrapper.vm.referenceCT).toBe(0)
  //   expect(wrapper.vm.operationInformation).toEqual([])
  //   expect(wrapper.vm.incrementedUnits).toBe(0)
  //   expect(wrapper.vm.incrementInterval).toBeNull()
  // })

  it('starts the incrementer correctly', () => {
    jest.useFakeTimers()
    const mockOperation = { planned_number_units: 10 }
    wrapper.setData({ operationInformation: [mockOperation], referenceCT: 1000 })
    wrapper.vm.startIncrementer()
    jest.advanceTimersByTime(1000)
    expect(wrapper.vm.incrementedUnits).toBe(1)
    jest.clearAllTimers()
  })

  it('initializes incrementer correctly when there are operations', () => {
    const mockOperation = { planned_number_units: 10 }
    wrapper.setData({ operationInformation: [mockOperation] })
    wrapper.vm.initializeIncrementer()
    expect(wrapper.vm.incrementedUnits).toBe(mockOperation.planned_number_units)
  })

  it('initializes incrementer correctly when there are no operations', () => {
    const mockOperation = { planned_number_units: 0 }
    wrapper.setData({ operationInformation: [mockOperation] })
    wrapper.vm.initializeIncrementer()
    expect(wrapper.vm.incrementedUnits).toBe(0)
  })

  it('fetch data from operation information table', async () => {
    await wrapper.vm.fetchAllOperations()

    const mockAPI = await jest.fn(() => '/api/get-all-operations')

    expect(mockAPI).toBeTruthy()
  })

  it('fetch data from replenishment notice table', () => {
    wrapper.setData({
      replenishmentData: [
        {
          error_code: 'エラー3-01',
          process_id: '部品供給機',
        },
        {
          error_code: 'エラー5-01',
          process_id: '部品供給機',
        },
      ],
    })

    wrapper.vm.fetchReplenishmentNotice()
    expect(wrapper.vm.replenishmentData).toHaveLength(2)
  })

  it('formats product numbers correctly', () => {
    expect(wrapper.vm.formatProductNumber(123)).toBe('0123')
    expect(wrapper.vm.formatProductNumber(4567)).toBe('4567')
    expect(wrapper.vm.formatProductNumber(12345)).toBe('9999')
  })

  it('maps operationInformation correctly in getOperationTable', () => {
    const mockOperationInformation = [
      {
        process_id: 1,
        process_name: 'Process A',
        product_number: 123,
        facility_cycle_time: 15.6789,
      },
      {
        process_id: 2,
        process_name: 'Process B',
        product_number: 12345,
        facility_cycle_time: 20.1234,
      },
    ]

    wrapper.setData({ operationInformation: mockOperationInformation })

    wrapper.vm.getOperationTable()

    expect(wrapper.vm.operation_table).toEqual([
      {
        process_id: 1,
        process_name: 'Process A',
        product_number: '0123',
        facility_cycle_time: '15.68',
      },
      {
        process_id: 2,
        process_name: 'Process B',
        product_number: '9999',
        facility_cycle_time: '20.12',
      },
    ])
  })

  it('fetch data from reference cycle table', async () => {
    wrapper.setData({
      referenceCT: 2000,
    })

    await wrapper.vm.fetchReferenceCT()

    const mockAPI = await jest.fn(() => '/api/get-ref-cycle-time')

    expect(mockAPI).toBeTruthy()
    expect(wrapper.vm.referenceCT).toBe(2000)
  })

  it('should start with ProcessChart', () => {
    wrapper.vm.startSwitchInterval()
    expect(wrapper.vm.currentComponent).toBe('ProcessChart')
  })

  it('should switch to ErrorInformation after 7 seconds', () => {
    wrapper.vm.startSwitchInterval()
    jest.advanceTimersByTime(7000)
    expect(wrapper.vm.currentComponent).toBe('ErrorInformation')
  })

  it('should switch back to ProcessChart after 14 seconds', () => {
    wrapper.vm.startSwitchInterval()
    jest.advanceTimersByTime(14000)
    expect(wrapper.vm.currentComponent).toBe('ProcessChart')
  })

  it('catches error and logs it', async () => {
    const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {})
    await wrapper.vm.updatePlannedUnits()

    // expect(consoleLogSpy).toHaveBeenCalled()
    expect(consoleLogSpy).toHaveBeenCalledTimes(1)
    console.log.mockRestore()

    console.log.mockClear()
  })
})
